/**
 * Virtual Memory Optimizer - Frontend Logic
 * ==========================================
 * Handles SPA navigation, API communication, and dynamic DOM rendering.
 * Uses Fetch API for RESTful communication with Flask backend.
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

const API_BASE_URL = '/api';

// =============================================================================
// DOM ELEMENTS
// =============================================================================

// Tab Navigation
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Paging Form
const pagingForm = document.getElementById('paging-form');
const pagingAlgorithm = document.getElementById('paging-algorithm');
const pageReference = document.getElementById('page-reference');
const frameCount = document.getElementById('frame-count');
const pagingSubmit = document.getElementById('paging-submit');
const pagingResults = document.getElementById('paging-results');

// Allocation Form
const allocationForm = document.getElementById('allocation-form');
const allocationAlgorithm = document.getElementById('allocation-algorithm');
const memoryBlocks = document.getElementById('memory-blocks');
const processSizes = document.getElementById('process-sizes');
const allocationSubmit = document.getElementById('allocation-submit');
const allocationResults = document.getElementById('allocation-results');

// =============================================================================
// TAB NAVIGATION (SPA - No Page Reloads)
// =============================================================================

/**
 * Switch between Paging and Allocation tabs.
 * Uses event.preventDefault() to prevent any form submissions.
 */
tabButtons.forEach(button => {
    button.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default button behavior
        
        const targetTab = button.getAttribute('data-tab');
        
        // Update active button
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update active content
        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === `${targetTab}-section`) {
                content.classList.add('active');
            }
        });
    });
});

// =============================================================================
// PAGING SIMULATION
// =============================================================================

/**
 * Handle Paging Form Submission.
 * Prevents default form behavior and triggers async API call.
 */
pagingSubmit.addEventListener('click', (event) => {
    event.preventDefault(); // Prevent form hijacking
    
    const algorithm = pagingAlgorithm.value;
    const pageRef = pageReference.value.trim();
    const frames = parseInt(frameCount.value, 10);
    
    // Validation
    if (!pageRef) {
        showError(pagingResults, 'Please enter a page reference string');
        return;
    }
    
    if (!frames || frames < 1) {
        showError(pagingResults, 'Frame count must be at least 1');
        return;
    }
    
    // Run simulation
    runPagingSimulation(algorithm, pageRef, frames);
});

/**
 * Async function to fetch paging simulation results from Flask API.
 * @param {string} algorithm - FIFO, LRU, LIFO, or Optimal
 * @param {string} pageRefString - Comma-separated page references
 * @param {number} frameCount - Number of physical memory frames
 */
async function runPagingSimulation(algorithm, pageRefString, frameCount) {
    // Show loading state
    showLoading(pagingResults);
    
    try {
        const response = await fetch(`${API_BASE_URL}/paging`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                algorithm: algorithm,
                page_reference: pageRefString,
                frame_count: frameCount
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'API request failed');
        }
        
        const data = await response.json();
        
        // Render results
        renderPagingResults(data);
        
    } catch (error) {
        showError(pagingResults, error.message);
    }
}

/**
 * Render paging simulation results dynamically.
 * Builds DOM elements based on API response payload.
 * @param {Object} data - API response data
 */
function renderPagingResults(data) {
    let html = '';
    
    // Summary Cards
    html += `
        <div class="paging-summary">
            <div class="summary-card hits">
                <div class="label">Total Hits</div>
                <div class="value">${data.hits}</div>
            </div>
            <div class="summary-card faults">
                <div class="label">Total Faults</div>
                <div class="value">${data.faults}</div>
            </div>
            <div class="summary-card hit-ratio">
                <div class="label">Hit Ratio</div>
                <div class="value">${(data.hit_ratio * 100).toFixed(1)}%</div>
            </div>
            <div class="summary-card fault-ratio">
                <div class="label">Fault Ratio</div>
                <div class="value">${(data.fault_ratio * 100).toFixed(1)}%</div>
            </div>
        </div>
    `;
    
    // Step-by-Step Visualization
    html += '<div class="steps-container">';
    
    data.steps.forEach(step => {
        const actionClass = step.hit ? 'hit' : 'fault';
        const actionText = step.hit ? '✓ HIT' : '✗ FAULT';
        
        // Build frame boxes
        let framesHtml = '';
        for (let i = 0; i < data.frame_count; i++) {
            const page = step.frames_after[i];
            if (page !== undefined) {
                framesHtml += `<div class="frame-box filled">${page}</div>`;
            } else {
                framesHtml += `<div class="frame-box empty">-</div>`;
            }
        }
        
        html += `
            <div class="step-card">
                <div class="step-header">
                    <span class="step-number">Step ${step.step}</span>
                    <span class="step-page">Page: ${step.page}</span>
                    <span class="step-action ${actionClass}">${actionText}</span>
                </div>
                <div class="frame-display">
                    ${framesHtml}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    pagingResults.innerHTML = html;
}

// =============================================================================
// ALLOCATION SIMULATION
// =============================================================================

/**
 * Handle Allocation Form Submission.
 * Prevents default form behavior and triggers async API call.
 */
allocationSubmit.addEventListener('click', (event) => {
    event.preventDefault(); // Prevent form hijacking
    
    const algorithm = allocationAlgorithm.value;
    const blocks = memoryBlocks.value.trim();
    const processes = processSizes.value.trim();
    
    // Validation
    if (!blocks) {
        showError(allocationResults, 'Please enter memory block sizes');
        return;
    }
    
    if (!processes) {
        showError(allocationResults, 'Please enter process sizes');
        return;
    }
    
    // Run simulation
    runAllocationSimulation(algorithm, blocks, processes);
});

/**
 * Async function to fetch allocation simulation results from Flask API.
 * @param {string} algorithm - First Fit, Best Fit, Worst Fit, or Next Fit
 * @param {string} blockSizes - Comma-separated memory block sizes
 * @param {string} procSizes - Comma-separated process sizes
 */
async function runAllocationSimulation(algorithm, blockSizes, procSizes) {
    // Show loading state
    showLoading(allocationResults);
    
    try {
        const response = await fetch(`${API_BASE_URL}/allocation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                algorithm: algorithm,
                memory_blocks: blockSizes,
                process_sizes: procSizes
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'API request failed');
        }
        
        const data = await response.json();
        
        // Render results
        renderAllocationResults(data);
        
    } catch (error) {
        showError(allocationResults, error.message);
    }
}

/**
 * Render allocation simulation results dynamically.
 * Builds DOM elements including progress bars based on API response.
 * @param {Object} data - API response data
 */
function renderAllocationResults(data) {
    let html = '';
    
    // Fragmentation Summary
    html += `
        <div class="allocation-summary">
            <div class="fragmentation-card">
                <div class="label">Total Internal Fragmentation</div>
                <div class="value">${data.total_internal_fragmentation} KB</div>
            </div>
            <div class="fragmentation-card">
                <div class="label">Total External Fragmentation</div>
                <div class="value external">${data.total_external_fragmentation} KB</div>
            </div>
        </div>
    `;
    
    // Block Visualization with Progress Bars
    html += '<div class="blocks-container">';
    
    const totalMemory = data.block_status.reduce((sum, b) => sum + b.size, 0);
    
    data.block_status.forEach(block => {
        const allocatedSize = block.allocated_to ? (block.size - block.internal_frag) : 0;
        const internalFrag = block.internal_frag || 0;
        const freeSize = block.size - allocatedSize - internalFrag;
        
        // Calculate percentages for progress bar
        const allocatedPct = (allocatedSize / block.size) * 100;
        const fragPct = (internalFrag / block.size) * 100;
        const freePct = (freeSize / block.size) * 100;
        
        // Build progress bar segments
        let barSegments = '';
        
        if (allocatedSize > 0) {
            barSegments += `
                <div class="memory-bar-segment allocated" style="width: ${allocatedPct}%" title="Allocated: ${allocatedSize}KB">
                    ${block.allocated_to || ''}
                </div>
            `;
        }
        
        if (internalFrag > 0) {
            barSegments += `
                <div class="memory-bar-segment fragmentation" style="width: ${fragPct}%" title="Internal Fragmentation: ${internalFrag}KB">
                    IF
                </div>
            `;
        }
        
        if (freeSize > 0) {
            barSegments += `
                <div class="memory-bar-segment free" style="width: ${freePct}%" title="Free: ${freeSize}KB">
                    Free
                </div>
            `;
        }
        
        const statusText = block.allocated_to 
            ? `<span class="status-allocated">Allocated to ${block.allocated_to}</span>`
            : '<span class="status-not-allocated">Free</span>';
        
        html += `
            <div class="block-card">
                <div class="block-header">
                    <span class="block-id">Block ${block.id}</span>
                    <span class="block-size">${block.size} KB | ${statusText}</span>
                </div>
                <div class="memory-bar-container">
                    <div class="memory-bar-label">
                        <span>0 KB</span>
                        <span>${block.size} KB</span>
                    </div>
                    <div class="memory-bar">
                        ${barSegments}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Allocation Table
    html += `
        <table class="allocation-table">
            <thead>
                <tr>
                    <th>Process</th>
                    <th>Size (KB)</th>
                    <th>Block</th>
                    <th>Block Size (KB)</th>
                    <th>Internal Fragmentation (KB)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.allocation.forEach(alloc => {
        const status = alloc.status === 'NOT ALLOCATED' 
            ? '<span class="status-not-allocated">Not Allocated</span>'
            : '<span class="status-allocated">Allocated</span>';
        
        const blockDisplay = alloc.block !== null ? alloc.block : '-';
        const blockSizeDisplay = alloc.block_size !== null ? alloc.block_size : '-';
        const fragDisplay = alloc.internal_fragmentation !== null ? alloc.internal_fragmentation : '-';
        
        html += `
            <tr>
                <td>${alloc.process}</td>
                <td>${alloc.process_size}</td>
                <td>${blockDisplay}</td>
                <td>${blockSizeDisplay}</td>
                <td>${fragDisplay}</td>
                <td>${status}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    
    allocationResults.innerHTML = html;
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Show loading spinner in results container.
 * @param {HTMLElement} container - Results container element
 */
function showLoading(container) {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;
}

/**
 * Show error message in results container.
 * @param {HTMLElement} container - Results container element
 * @param {string} message - Error message to display
 */
function showError(container, message) {
    container.innerHTML = `
        <div class="error-message">
            <strong>Error:</strong> ${message}
        </div>
    `;
}

// =============================================================================
// INITIALIZATION
// =============================================================================

/**
 * Initialize the application.
 * Performs health check on API and sets up event listeners.
 */
async function init() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✓ API Connection Established');
        }
    } catch (error) {
        console.warn('⚠ API not available. Make sure Flask server is running on port 5000.');
    }
}

// Run initialization when DOM is ready
document.addEventListener('DOMContentLoaded', init);