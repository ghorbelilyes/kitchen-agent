package com.factory.kitchen.service.validation;

import com.factory.kitchen.dto.DimensionComparisonDto;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class RiskDetectionModule {
    
    private static final double CRITICAL_MISMATCH_THRESHOLD_MM = 20.0;

    public void detectRisks(List<DimensionComparisonDto> comparisons, List<String> globalRisks) {
        for (DimensionComparisonDto comp : comparisons) {
            if ("MISSING".equals(comp.status)) {
                comp.riskNote = "Critical measurement missing from site survey.";
                globalRisks.add(comp.label + " is missing.");
            } else if ("UNREADABLE".equals(comp.status)) {
                comp.riskNote = "Plan dimension was unreadable. Relying entirely on site measurement.";
            } else if ("MISMATCHED".equals(comp.status)) {
                if (comp.difference != null && comp.difference > CRITICAL_MISMATCH_THRESHOLD_MM) {
                    comp.riskNote = "CRITICAL: Mismatch exceeds 20mm tolerance. Cabinet collision highly likely.";
                    globalRisks.add(comp.label + " has a critical mismatch of " + comp.difference + "mm.");
                } else {
                    comp.riskNote = "Minor mismatch detected. Verify filler panels are sufficient.";
                }
            }
        }
    }
}
