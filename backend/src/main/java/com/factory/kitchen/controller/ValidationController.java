package com.factory.kitchen.controller;

import com.factory.kitchen.dto.*;
import com.factory.kitchen.service.validation.ValidationEngineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/projects/{projectId}/validation")
@CrossOrigin(origins = "*")
public class ValidationController {

    @Autowired
    private ValidationEngineService validationEngineService;

    public static class ValidationRequest {
        public List<PlanDimensionDto> planDimensions;
        public List<SiteMeasurementDto> siteMeasurements;
    }

    @PostMapping("/compare")
    public ResponseEntity<ValidationReportDto> compareSiteMeasurements(
            @PathVariable String projectId,
            @RequestBody ValidationRequest request) {
        
        ValidationReportDto report = validationEngineService.runValidation(
            projectId, 
            request.planDimensions, 
            request.siteMeasurements
        );
        
        return ResponseEntity.ok(report);
    }
}
