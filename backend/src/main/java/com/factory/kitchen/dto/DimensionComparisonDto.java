package com.factory.kitchen.dto;

public class DimensionComparisonDto {
    public String dimensionId;
    public String label;
    public Double expected;
    public Double actual;
    public String status; // MATCHED, MISMATCHED, MISSING, UNREADABLE
    public Double difference;
    public boolean requiresRemeasurement;
    public String riskNote;
}
