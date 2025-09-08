const API_BASE = 'http://localhost:8000';

// 1. Generate TechSpec
async function generateTechSpec(repoPath, acUrl, figmaUrl) {
    const response = await fetch(`${API_BASE}/generate-techspec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            repo_path: repoPath,
            ac_google_doc_export_url: acUrl,
            figma_file_url: figmaUrl
        })
    });
    return await response.json();
}

// 2. Generate Tagging
async function generateTagging() {
    const response = await fetch(`${API_BASE}/suggest-tagging`, {
        method: 'POST'
    });
    return await response.json();
}

// 3. Apply Tagging
async function applyTagging() {
    const response = await fetch(`${API_BASE}/apply-tagging`, {
        method: 'POST'
    });
    return await response.json();
}

// 4. Rollback Changes
async function rollbackChanges() {
    const response = await fetch(`${API_BASE}/rollback-changes`, {
        method: 'POST'
    });
    return await response.json();
}

// 5. Get Status
async function getStatus() {
    const response = await fetch(`${API_BASE}/status`);
    return await response.json();
}