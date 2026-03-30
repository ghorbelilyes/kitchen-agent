package com.factory.kitchen.service.validation;

import com.factory.kitchen.dto.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class ValidationEngineService {

    @Autowired
    private DimensionComparisonModule comparisonModule;
    
    @Autowired
    private RiskDetectionModule riskModule;
    
    @Autowired
    private FinalDecisionModule decisionModule;

    public ValidationReportDto runValidation(String projectId, List<PlanDimensionDto> planDims, List<SiteMeasurementDto> siteDims) {
        ValidationReportDto report = new ValidationReportDto();
        report.projectId = projectId;
        report.comparisons = new ArrayList<>();
        report.globalRisks = new ArrayList<>();
        report.totalDimensions = planDims.size();
        
        int mismatched = 0;

        for (PlanDimensionDto plan : planDims) {
            // Find matching site measurement
            SiteMeasurementDto matchingSite = siteDims.stream()
                .filter(s -> s.id.equals(plan.id))
                .findFirst()
                .orElse(null);

            // 1. Compare
            DimensionComparisonDto comp = comparisonModule.compare(plan, matchingSite);
            
            if ("MISMATCHED".equals(comp.status)) {
                mismatched++;
            }
            
            report.comparisons.add(comp);
        }

        report.mismatchedCount = mismatched;

        // 2. Detect Risks
        riskModule.detectRisks(report.comparisons, report.globalRisks);

        // 3. Final Decision
        report.finalDecision = decisionModule.calculateDecision(report.comparisons);

        return report;
    }
}
