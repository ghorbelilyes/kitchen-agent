package com.factory.kitchen.service.validation;

import com.factory.kitchen.dto.DimensionComparisonDto;
import com.factory.kitchen.dto.PlanDimensionDto;
import com.factory.kitchen.dto.SiteMeasurementDto;
import org.springframework.stereotype.Component;

@Component
public class DimensionComparisonModule {
    
    private static final double TOLERANCE_MM = 5.0;
    
    public DimensionComparisonDto compare(PlanDimensionDto plan, SiteMeasurementDto site) {
        DimensionComparisonDto result = new DimensionComparisonDto();
        result.dimensionId = plan.id;
        result.label = plan.label;
        result.expected = plan.expectedValue;
        
        if (site == null) {
            result.status = "MISSING";
            result.requiresRemeasurement = true;
            return result;
        }
        
        result.actual = site.actualValue;
        
        if (plan.isUnreadable || plan.expectedValue == null) {
            result.status = "UNREADABLE";
            result.requiresRemeasurement = false; // We have the site value now
            return result;
        }

        double diff = Math.abs(plan.expectedValue - site.actualValue);
        result.difference = diff;
        
        if (diff <= TOLERANCE_MM) {
            result.status = "MATCHED";
            result.requiresRemeasurement = false;
        } else {
            result.status = "MISMATCHED";
            result.requiresRemeasurement = false;
        }
        
        return result;
    }
}
