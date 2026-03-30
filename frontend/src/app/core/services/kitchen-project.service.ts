import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PlanDimension, SiteMeasurement, ValidationReport } from '../models/validation.models';

@Injectable({
    providedIn: 'root'
})
export class KitchenProjectService {
    private http = inject(HttpClient);
    private apiUrl = '/api/projects';

    uploadPlanImage(file: File): Observable<{ projectId: string, extractedDimensions: PlanDimension[] }> {
        const formData = new FormData();
        formData.append('file', file);
        return this.http.post<any>(`${this.apiUrl}/upload-plan`, formData);
    }

    submitSiteMeasurements(projectId: string, measurements: SiteMeasurement[]): Observable<ValidationReport> {
        return this.http.post<ValidationReport>(`${this.apiUrl}/${projectId}/measurements`, { measurements });
    }

    getValidationReport(projectId: string): Observable<ValidationReport> {
        return this.http.get<ValidationReport>(`${this.apiUrl}/${projectId}/report`);
    }
}
