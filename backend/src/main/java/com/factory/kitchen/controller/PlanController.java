package com.factory.kitchen.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/projects")
@CrossOrigin(origins = "*")
public class PlanController {

    @Autowired
    private RestTemplate restTemplate;

    @PostMapping("/upload-plan")
    public ResponseEntity<Map<String, Object>> uploadPlan(@RequestParam("file") MultipartFile file) {
        try {
            // Forward the file to the Python Agent
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", file.getResource());

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
            
            String agentUrl = "http://localhost:8000/api/vision/analyze-plan";
            ResponseEntity<Map> agentResponse = restTemplate.postForEntity(agentUrl, requestEntity, Map.class);

            String projectId = UUID.randomUUID().toString();
            
            return ResponseEntity.ok(Map.of(
                "message", "Plan analyzed successfully",
                "projectId", projectId,
                "agentData", agentResponse.getBody()
            ));

        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("error", "Failed to communicate with Agent", "details", e.getMessage()));
        }
    }
}
