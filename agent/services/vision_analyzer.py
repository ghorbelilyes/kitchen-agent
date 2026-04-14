import asyncio
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

NODE20_BIN = Path("/home/ilyes/.nvm/versions/node/v20.20.0/bin")
PI_NODE_MODULE = Path(
    "/home/ilyes/.nvm/versions/node/v20.20.0/lib/node_modules/@mariozechner/pi-coding-agent/dist/index.js"
)
PI_MODEL_RESOLVER_MODULE = Path(
    "/home/ilyes/.nvm/versions/node/v20.20.0/lib/node_modules/@mariozechner/pi-coding-agent/dist/core/model-resolver.js"
)
PI_AUTH_PATH = Path.home() / ".pi" / "agent" / "auth.json"
PI_SETTINGS_PATH = Path.home() / ".pi" / "agent" / "settings.json"


def _resolve_pi_runtime() -> tuple[str, str, Dict[str, str]]:
    node_executable = str(NODE20_BIN / "node")
    pi_executable = str(NODE20_BIN / "pi")

    if not os.path.exists(node_executable) or not os.path.exists(pi_executable):
        node_executable = shutil.which("node") or "node"
        pi_executable = shutil.which("pi") or "pi"

    custom_env = dict(os.environ)
    custom_env["PATH"] = f"{NODE20_BIN}:{custom_env.get('PATH', '')}"
    custom_env["PI_AUTH_PATH"] = str(PI_AUTH_PATH)
    custom_env["PI_SETTINGS_PATH"] = str(PI_SETTINGS_PATH)

    return node_executable, pi_executable, custom_env


async def list_available_pi_models() -> Dict[str, Any]:
    logger.info("Loading available Pi models from the local model registry...")

    node_executable, _, custom_env = _resolve_pi_runtime()
    sdk_module_uri = PI_NODE_MODULE.resolve().as_uri()
    model_resolver_uri = PI_MODEL_RESOLVER_MODULE.resolve().as_uri()

    script = """
import fs from "fs";
import { AuthStorage, ModelRegistry } from "__SDK_MODULE__";
import { defaultModelPerProvider } from "__MODEL_RESOLVER__";

function readJson(path) {
    if (!path) return {};
    try {
        return JSON.parse(fs.readFileSync(path, "utf8"));
    } catch {
        return {};
    }
}

function toValue(model) {
    return model.provider + "/" + model.id;
}

const authData = readJson(process.env.PI_AUTH_PATH);
const settingsData = readJson(process.env.PI_SETTINGS_PATH);
const authStorage = AuthStorage.inMemory(authData);
const registry = ModelRegistry.create(authStorage);
const availableModels = [...registry.getAvailable()].sort((a, b) => {
    const providerCmp = a.provider.localeCompare(b.provider);
    if (providerCmp !== 0) return providerCmp;
    return a.id.localeCompare(b.id);
});

let defaultValue = null;

if (settingsData.defaultProvider && settingsData.defaultModel) {
    const settingsMatch = availableModels.find(
        (model) => model.provider === settingsData.defaultProvider && model.id === settingsData.defaultModel
    );
    if (settingsMatch) defaultValue = toValue(settingsMatch);
}

if (!defaultValue) {
    for (const provider of Object.keys(defaultModelPerProvider)) {
        const defaultId = defaultModelPerProvider[provider];
        const match = availableModels.find((model) => model.provider === provider && model.id === defaultId);
        if (match) {
            defaultValue = toValue(match);
            break;
        }
    }
}

if (!defaultValue && availableModels.length > 0) {
    defaultValue = toValue(availableModels[0]);
}

const models = availableModels.map((model) => ({
    value: toValue(model),
    provider: model.provider,
    model: model.id,
    name: model.name ?? model.id,
    reasoning: Boolean(model.reasoning),
    supportsImages: Array.isArray(model.input) && model.input.includes("image"),
    contextWindow: model.contextWindow ?? null,
    maxTokens: model.maxTokens ?? null,
}));

console.log(JSON.stringify({ defaultModel: defaultValue, models }));
""".replace("__SDK_MODULE__", sdk_module_uri).replace("__MODEL_RESOLVER__", model_resolver_uri)

    process = await asyncio.create_subprocess_exec(
        node_executable,
        "--input-type=module",
        "-e",
        script,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=custom_env,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_message = stderr.decode().strip()
        logger.error(f"Pi model registry lookup failed: {error_message}")
        raise Exception(f"Failed to load Pi models: {error_message}")

    result = json.loads(stdout.decode().strip() or '{"defaultModel": null, "models": []}')
    logger.info(f"Loaded {len(result.get('models', []))} Pi models.")
    return result


async def extract_plan_dimensions(
    image_bytes: bytes, filename: str, model: Optional[str] = None
) -> Dict[str, Any]:
    logger.info(f"Dynamically analyzing {filename} using the local 'pi' CLI agent...")
    
    # Save the bytes to a temporary file so 'pi' can read it
    temp_path = f"/tmp/pi_upload_{filename}"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)

    # The strict prompt for the pi agent — summarized practical dimensions
    prompt = (
        "Analyze this kitchen plan image and extract a SUMMARIZED JSON with these exact fields:\n"
        "\n"
        "1. 'layout_type': string (L-shaped, U-shaped, Straight, etc.)\n"
        "2. 'visible_elements': list of strings (cabinets, appliances, sink, hood, etc.)\n"
        "3. 'risky_areas': list of strings (production risks)\n"
        "4. 'dimensions': array of summarized measurements. ONLY include these categories:\n"
        "\n"
        "   category 'wall' — total wall lengths only:\n"
        "     - Left wall total length\n"
        "     - Right wall total length (if exists)\n"
        "     - Top/back wall total length\n"
        "     - Wall height\n"
        "\n"
        "   category 'height' — key vertical dimensions only:\n"
        "     - Upper cabinets height\n"
        "     - Backsplash zone height (distance between upper cabinets bottom and countertop)\n"
        "     - Countertop height from floor\n"
        "\n"
        "   category 'plumbing' — plumbing installation interval:\n"
        "     - Plumbing under sink FROM (distance from left wall edge to start of sink plumbing zone, in mm)\n"
        "     - Plumbing under sink TO (distance from left wall edge to end of sink plumbing zone, in mm)\n"
        "\n"
        "   category 'electrical' — electrical installation interval:\n"
        "     - Hood electrical FROM (distance from left wall edge to start of hood zone, in mm)\n"
        "     - Hood electrical TO (distance from left wall edge to end of hood zone, in mm)\n"
        "\n"
        "Each dimension object must have: id, label, expectedValue (number or null), unit (mm), isUnreadable (boolean), category (string: wall/height/plumbing/electrical).\n"
        "\n"
        "RULES:\n"
        "- Do NOT list every individual cabinet width. Only TOTAL wall lengths.\n"
        "- For plumbing/electrical, calculate the interval position from the left wall edge.\n"
        "- If a value is unreadable, set expectedValue to null and isUnreadable to true.\n"
        "- Maximum 11 dimensions total.\n"
        "- ONLY output valid JSON, absolutely no markdown formatting or backticks."
    )

    try:
        node_executable, pi_executable, custom_env = _resolve_pi_runtime()
            
        # Run pi in non-interactive print mode, attaching the image
        cmd = [
            node_executable,
            pi_executable,
            "--no-tools",
            "--no-skills",
            "--no-extensions",
            "--no-session",
        ]

        if model and model.strip():
            cmd.extend(["--model", model.strip()])

        cmd.extend(["-p", f"@{temp_path}", prompt])
        
        logger.info(f"Running command: {' '.join(cmd)}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=custom_env
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Pi CLI failed: {stderr.decode()}")
            raise Exception(f"Failed to run pi CLI: {stderr.decode()}")
            
        raw_output = stdout.decode().strip()
        
        # Clean up potential markdown formatting just in case the LLM disobeys
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
            
        result_json = json.loads(raw_output.strip())
        logger.info("Successfully extracted dynamic JSON from pi CLI!")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return result_json

    except Exception as e:
        logger.error(f"Error extracting dimensions: {e}")
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return {"error": str(e), "message": "Could not parse JSON from pi CLI output"}
