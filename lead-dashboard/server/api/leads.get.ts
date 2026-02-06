import fs from 'fs';
import path from 'path';
import { defineEventHandler } from 'h3';

export default defineEventHandler(async (event) => {
    const jsonlPath = path.resolve(process.cwd(), '../lead-analyzer/output/leads_analyzed.jsonl');

    try {
        if (!fs.existsSync(jsonlPath)) {
            return { leads: [], error: 'Data file not found' };
        }

        const fileContent = fs.readFileSync(jsonlPath, 'utf-8');
        const lines = fileContent.split('\n');
        const leads = [];

        for (const line of lines) {
            if (!line.trim()) continue;
            try {
                leads.push(JSON.parse(line));
            } catch (e) {
                console.error('Error parsing line:', e);
            }
        }

        // Sort by recent processing or score? Let's sort by processed_at descending by default
        leads.sort((a, b) => new Date(b.processed_at).getTime() - new Date(a.processed_at).getTime());

        return { leads };
    } catch (error) {
        console.error('API Error:', error);
        return { leads: [], error: 'Internal Server Error' };
    }
});
