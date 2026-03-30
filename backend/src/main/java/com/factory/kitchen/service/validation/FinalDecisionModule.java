package com.factory.kitchen.service.validation;

import com.factory.kitchen.dto.DimensionComparisonDto;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class FinalDecisionModule {

    public String calculateDecision(List<DimensionComparisonDto> comparisons) {
        boolean hasMissing = false;
        boolean hasCriticalMismatch = false;

        for (DimensionComparisonDto comp : comparisons) {
            if ("MISSING".equals(comp.status)) {
                hasMissing = true;
            }
            if ("MISMATCHED".equals(comp.status) && comp.difference != null && comp.difference > 20.0) {
                hasCriticalMismatch = true;
            }
        }

        if (hasMissing) {
            return "NEEDS_SITE_REMEASUREMENT";
        }
        
        if (hasCriticalMismatch) {
            return "NEEDS_CORRECTION";
        }

        return "APPROVED_FOR_DESIGN";
    }
}
