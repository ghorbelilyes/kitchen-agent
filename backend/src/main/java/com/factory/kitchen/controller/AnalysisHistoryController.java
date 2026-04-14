package com.factory.kitchen.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/analyses")
@CrossOrigin(origins = "*")
public class AnalysisHistoryController {

    private static final String AGENT_BASE_URL = "http://localhost:8000/api/vision/analyses";

    @Autowired
    private RestTemplate restTemplate;

    @GetMapping
    public ResponseEntity<List> listAnalyses() {
        try {
            ResponseEntity<List> response = restTemplate.getForEntity(AGENT_BASE_URL, List.class);
            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(List.of(Map.of("error", "Failed to fetch analyses: " + e.getMessage())));
        }
    }

    @GetMapping("/{analysisId}")
    public ResponseEntity<Map> getAnalysis(@PathVariable String analysisId) {
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(
                AGENT_BASE_URL + "/" + analysisId, Map.class);
            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("error", "Failed to fetch analysis: " + e.getMessage()));
        }
    }

    @DeleteMapping("/{analysisId}")
    public ResponseEntity<Map> deleteAnalysis(@PathVariable String analysisId) {
        try {
            restTemplate.delete(AGENT_BASE_URL + "/" + analysisId);
            return ResponseEntity.ok(Map.of("message", "Analysis deleted successfully", "id", analysisId));
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("error", "Failed to delete analysis: " + e.getMessage()));
        }
    }
}
