export interface PlanDimension {
    id: string;
    label: string; // e.g. "Total Wall Length", "Window Position"
    expectedValue: number | null; // null if UNREADABLE
    unit: 'mm' | 'cm' | 'inch';
    isUnreadable: boolean;
}

export interface SiteMeasurement {
    id: string;
    label: string;
    actualValue: number;
    unit: 'mm' | 'cm' | 'inch';
}

export type MatchStatus = 'MATCHED' | 'MISMATCHED' | 'MISSING' | 'IMPOSSIBLE' | 'RISKY';

export interface DimensionComparison {
    dimensionId: string;
    label: string;
    expected: number | null;
    actual: number;
    status: MatchStatus;
    difference: number | null;
    requiresRemeasurement: boolean;
    riskNote?: string;
}

export type FinalDecision = 'APPROVED_FOR_DESIGN' | 'NEEDS_CORRECTION' | 'NEEDS_SITE_REMEASUREMENT';

export interface ValidationReport {
    projectId: string;
    totalDimensions: number;
    mismatchedCount: number;
    comparisons: DimensionComparison[];
    finalDecision: FinalDecision;
    notes: string[];
}
