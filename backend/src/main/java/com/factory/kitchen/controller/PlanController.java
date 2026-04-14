package com.factory.kitchen.controller;

import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.http.MediaTypeFactory;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.util.UriUtils;
import org.springframework.web.multipart.MultipartFile;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/projects")
@CrossOrigin(origins = "*")
public class PlanController {

    private static final String AGENT_VISION_BASE_URL = "http://localhost:8000/api/vision";
    private static final String UPLOAD_DIR = "/home/ilyes/custom projects/kitchen-validator/kitchen-app/uploads";

    @Autowired
    private RestTemplate restTemplate;

    @PostMapping("/upload-plan")
    public ResponseEntity<Map<String, Object>> uploadPlan(
        @RequestParam("file") MultipartFile file,
        @RequestParam(value = "model", required = false) String model
    ) {
        try {
            String originalFilename = file.getOriginalFilename() != null
                ? file.getOriginalFilename()
                : "kitchen-plan";
            String storedFilename = UUID.randomUUID() + getFileExtension(originalFilename);

            Path uploadPath = Paths.get(UPLOAD_DIR);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }
            Path targetLocation = uploadPath.resolve(storedFilename);
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("File saved successfully to: " + targetLocation.toString());

            // 2. Forward the file to the Python Agent
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", file.getResource());
            body.add("stored_filename", storedFilename);
            if (model != null && !model.isBlank()) {
                body.add("model", model);
            }

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
            
            String agentUrl = AGENT_VISION_BASE_URL + "/analyze-plan";
            ResponseEntity<Map> agentResponse = restTemplate.postForEntity(agentUrl, requestEntity, Map.class);
            Map<String, Object> agentBody = agentResponse.getBody() != null ? agentResponse.getBody() : Map.of();

            String projectId = UUID.randomUUID().toString();
            String imageUrl = buildUploadUrl(storedFilename);
            Map<String, Object> responseBody = new HashMap<>();
            responseBody.put("message", "Plan analyzed successfully");
            responseBody.put("projectId", projectId);
            responseBody.put("savedPath", targetLocation.toString());
            responseBody.put("imageFilename", storedFilename);
            responseBody.put("imageUrl", imageUrl);
            responseBody.put("agentData", agentBody);
            
            return ResponseEntity.ok(responseBody);

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("error", "Failed to process upload", "details", e.getMessage()));
        }
    }

    @GetMapping("/models")
    public ResponseEntity<Map> getAvailableModels() {
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(
                AGENT_VISION_BASE_URL + "/models", Map.class
            );
            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(
                Map.of("error", "Failed to load Pi models", "details", e.getMessage())
            );
        }
    }

    @GetMapping("/uploads/{filename:.+}")
    public ResponseEntity<Resource> getUploadedFile(@PathVariable String filename) {
        try {
            Path uploadRoot = Paths.get(UPLOAD_DIR).toAbsolutePath().normalize();
            Path filePath = uploadRoot.resolve(filename).normalize();
            if (!filePath.startsWith(uploadRoot) || !Files.exists(filePath) || !Files.isRegularFile(filePath)) {
                throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Uploaded file not found.");
            }

            Resource resource = new UrlResource(filePath.toUri());
            MediaType mediaType = MediaTypeFactory.getMediaType(resource)
                .orElse(MediaType.APPLICATION_OCTET_STREAM);

            return ResponseEntity.ok()
                .contentType(mediaType)
                .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"" + filePath.getFileName() + "\"")
                .body(resource);
        } catch (ResponseStatusException ex) {
            throw ex;
        } catch (Exception ex) {
            throw new ResponseStatusException(
                HttpStatus.INTERNAL_SERVER_ERROR,
                "Failed to load uploaded file.",
                ex
            );
        }
    }

    private String buildUploadUrl(String storedFilename) {
        return "http://localhost:8080/api/projects/uploads/"
            + UriUtils.encodePathSegment(storedFilename, StandardCharsets.UTF_8);
    }

    private String getFileExtension(String filename) {
        int dotIndex = filename.lastIndexOf('.');
        if (dotIndex < 0) {
            return "";
        }
        return filename.substring(dotIndex);
    }
}
