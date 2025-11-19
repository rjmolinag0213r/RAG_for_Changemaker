// API Base URL
const API_BASE = '/api';

// Tab Switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load data for specific tabs
    if (tabName === 'query') {
        loadStats();
    } else if (tabName === 'manage') {
        loadDocuments();
    }
}

// Submit Query
async function submitQuery() {
    const question = document.getElementById('question-input').value.trim();
    const nResults = parseInt(document.getElementById('n-results').value);
    const returnSources = document.getElementById('return-sources').checked;
    
    if (!question) {
        alert('Please enter a question');
        return;
    }
    
    // Show loading state
    setButtonLoading('query-btn-text', 'query-spinner', true);
    
    try {
        const response = await fetch(`${API_BASE}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                n_results: nResults,
                return_sources: returnSources
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error processing query');
        }
        
        displayAnswer(data);
        
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    } finally {
        setButtonLoading('query-btn-text', 'query-spinner', false);
    }
}

// Display Answer
function displayAnswer(data) {
    const answerSection = document.getElementById('answer-section');
    const answerText = document.getElementById('answer-text');
    const sourcesSection = document.getElementById('sources-section');
    const sourcesList = document.getElementById('sources-list');
    
    // Show answer
    answerText.textContent = data.answer;
    answerSection.style.display = 'block';
    
    // Show sources if available
    if (data.sources && data.sources.length > 0) {
        sourcesList.innerHTML = '';
        data.sources.forEach((source, index) => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.innerHTML = `
                <div class="source-header">
                    <span class="source-metadata">
                        <strong>Source ${index + 1}:</strong> ${source.metadata.source || 'Unknown'}
                    </span>
                    <span class="relevance-score">Score: ${source.relevance_score}</span>
                </div>
                <div class="source-text">${source.text}</div>
            `;
            sourcesList.appendChild(sourceItem);
        });
        sourcesSection.style.display = 'block';
    } else {
        sourcesSection.style.display = 'none';
    }
    
    // Scroll to answer
    answerSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Upload PDF
document.getElementById('pdf-input')?.addEventListener('change', async (e) => {
    const files = e.target.files;
    if (files.length === 0) return;
    
    const resultsDiv = document.getElementById('upload-results');
    const resultsContent = document.getElementById('upload-results-content');
    resultsContent.innerHTML = '<p>Uploading files...</p>';
    resultsDiv.style.display = 'block';
    
    const results = [];
    
    for (const file of files) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${API_BASE}/upload-pdf`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Upload failed');
            }
            
            results.push({
                success: true,
                filename: file.name,
                message: data.message,
                numChunks: data.num_chunks
            });
            
        } catch (error) {
            results.push({
                success: false,
                filename: file.name,
                message: error.message
            });
        }
    }
    
    displayUploadResults(results);
    
    // Clear file input
    e.target.value = '';
});

// Display Upload Results
function displayUploadResults(results) {
    const resultsContent = document.getElementById('upload-results-content');
    resultsContent.innerHTML = '';
    
    results.forEach(result => {
        const alertClass = result.success ? 'alert-success' : 'alert-error';
        const resultDiv = document.createElement('div');
        resultDiv.className = `alert ${alertClass}`;
        resultDiv.innerHTML = `
            <strong>${result.filename}</strong><br>
            ${result.message}
            ${result.numChunks ? `<br>Chunks created: ${result.numChunks}` : ''}
        `;
        resultsContent.appendChild(resultDiv);
    });
}

// Scrape URL
async function scrapeURL() {
    const url = document.getElementById('url-input').value.trim();
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    // Show loading state
    setButtonLoading('scrape-btn-text', 'scrape-spinner', true);
    
    try {
        const response = await fetch(`${API_BASE}/scrape-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Scraping failed');
        }
        
        displayScrapeResults(data);
        
        // Clear input
        document.getElementById('url-input').value = '';
        
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    } finally {
        setButtonLoading('scrape-btn-text', 'scrape-spinner', false);
    }
}

// Display Scrape Results
function displayScrapeResults(data) {
    const resultsDiv = document.getElementById('scrape-results');
    const resultsContent = document.getElementById('scrape-results-content');
    
    resultsContent.innerHTML = `
        <div class="alert alert-success">
            <strong>Success!</strong><br>
            ${data.message}<br>
            ${data.title ? `Title: ${data.title}<br>` : ''}
            Chunks created: ${data.num_chunks}
        </div>
    `;
    
    resultsDiv.style.display = 'block';
}

// Load Documents
async function loadDocuments() {
    const docsList = document.getElementById('documents-list');
    docsList.innerHTML = '<p>Loading documents...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/documents`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load documents');
        }
        
        if (data.total_documents === 0) {
            docsList.innerHTML = '<p>No documents indexed yet. Upload PDFs or scrape URLs to get started.</p>';
            return;
        }
        
        // Group documents by source
        const groupedDocs = {};
        data.documents.forEach(doc => {
            const source = doc.metadata.source || 'Unknown';
            if (!groupedDocs[source]) {
                groupedDocs[source] = [];
            }
            groupedDocs[source].push(doc);
        });
        
        docsList.innerHTML = '';
        
        Object.keys(groupedDocs).forEach(source => {
            const docs = groupedDocs[source];
            const sourceDiv = document.createElement('div');
            sourceDiv.className = 'document-item';
            sourceDiv.innerHTML = `
                <div class="document-info">
                    <div class="document-source">${source}</div>
                    <div class="document-text">
                        ${docs.length} chunks | 
                        Type: ${docs[0].metadata.source_type || 'unknown'}
                    </div>
                </div>
                <div class="document-actions">
                    <button class="btn btn-danger btn-small" onclick="deleteSource('${source}')">
                        Delete All
                    </button>
                </div>
            `;
            docsList.appendChild(sourceDiv);
        });
        
    } catch (error) {
        docsList.innerHTML = `<p class="alert alert-error">Error: ${error.message}</p>`;
    }
}

// Delete Document Source
async function deleteSource(source) {
    if (!confirm(`Are you sure you want to delete all documents from "${source}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/documents/source/${encodeURIComponent(source)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Delete failed');
        }
        
        showAlert(data.message, 'success');
        loadDocuments();
        
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    }
}

// Clear All Documents
async function clearAllDocuments() {
    if (!confirm('Are you sure you want to delete ALL documents? This cannot be undone!')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/clear`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Clear failed');
        }
        
        showAlert(data.message, 'success');
        loadDocuments();
        
    } catch (error) {
        showAlert('Error: ' + error.message, 'error');
    }
}

// Load Statistics
async function loadStats() {
    const statsContent = document.getElementById('stats-content');
    
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load stats');
        }
        
        statsContent.innerHTML = `
            <p>📚 <strong>Total Documents:</strong> ${data.total_documents}</p>
            <p>📖 <strong>Unique Sources:</strong> ${data.unique_sources}</p>
            ${data.sources.length > 0 ? `
                <p><strong>Sources:</strong></p>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    ${data.sources.map(s => `<li>${s}</li>`).join('')}
                </ul>
            ` : ''}
        `;
        
    } catch (error) {
        statsContent.innerHTML = `<p>Error loading stats: ${error.message}</p>`;
    }
}

// Utility Functions
function setButtonLoading(textId, spinnerId, isLoading) {
    const textElement = document.getElementById(textId);
    const spinnerElement = document.getElementById(spinnerId);
    
    if (isLoading) {
        textElement.style.display = 'none';
        spinnerElement.style.display = 'inline-block';
    } else {
        textElement.style.display = 'inline';
        spinnerElement.style.display = 'none';
    }
}

function showAlert(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass}`;
    alertDiv.textContent = message;
    
    // Find the active tab
    const activeTab = document.querySelector('.tab-content.active .card');
    if (activeTab) {
        activeTab.insertBefore(alertDiv, activeTab.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Drag and Drop for PDF Upload
const uploadArea = document.getElementById('upload-area');

uploadArea?.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.background = '#f8f9fa';
});

uploadArea?.addEventListener('dragleave', () => {
    uploadArea.style.background = '';
});

uploadArea?.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.background = '';
    
    const files = Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf');
    
    if (files.length > 0) {
        const pdfInput = document.getElementById('pdf-input');
        const dataTransfer = new DataTransfer();
        files.forEach(file => dataTransfer.items.add(file));
        pdfInput.files = dataTransfer.files;
        
        // Trigger change event
        pdfInput.dispatchEvent(new Event('change'));
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
});

// Enter key support for query
document.getElementById('question-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        submitQuery();
    }
});

// Enter key support for URL scraping
document.getElementById('url-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        scrapeURL();
    }
});
