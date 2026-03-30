import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatchStatus } from '../../models/validation.models';

@Component({
    selector: 'app-status-pill',
    standalone: true,
    imports: [CommonModule],
    template: `
        <span [class]="getStatusClass()" class="px-3 py-1 rounded-full text-sm font-medium">
            {{ getLabel() }}
        </span>
    `
})
export class StatusPillComponent {
    @Input() status!: MatchStatus | 'UNREADABLE';
    @Input() label?: string;

    getLabel(): string {
        if (this.label) return this.label;
        return this.status.replace('_', ' ');
    }

    getStatusClass(): string {
        const classes: Record<string, string> = {
            'MATCHED': 'bg-green-100 text-green-800',
            'MISMATCHED': 'bg-red-100 text-red-800',
            'MISSING': 'bg-yellow-100 text-yellow-800',
            'IMPOSSIBLE': 'bg-red-200 text-red-900 font-bold',
            'RISKY': 'bg-orange-100 text-orange-800',
            'UNREADABLE': 'bg-gray-200 text-gray-800'
        };
        return classes[this.status] || 'bg-gray-100 text-gray-800';
    }
}
