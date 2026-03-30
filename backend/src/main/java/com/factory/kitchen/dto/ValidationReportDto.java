package com.factory.kitchen.dto;

import java.util.List;

public class ValidationReportDto {
    public String projectId;
    public int totalDimensions;
    public int mismatchedCount;
    public List<DimensionComparisonDto> comparisons;
    public String finalDecision; // APPROVED_FOR_DESIGN, NEEDS_CORRECTION, NEEDS_SITE_REMEASUREMENT
    public List<String> globalRisks;
}
