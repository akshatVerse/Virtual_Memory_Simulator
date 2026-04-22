"""
Virtual Memory Optimization Simulator - Backend API
=====================================================
Implements Demand Paging and Memory Allocation algorithms.
"""

from flask import Flask, request, jsonify, send_from_directory, make_response, render_template
from collections import OrderedDict
import os

import os
app = Flask(__name__, template_folder='templates', static_folder='static')

# CORS headers for all responses


# Home route for Render deployment
@app.route('/')
def home():
    return render_template('index.html')


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Handle OPTIONS preflight requests
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return make_response('', 204)

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# DEMAND PAGING ALGORITHMS
# =============================================================================

def simulate_fifo(page_ref_string, frame_count):
    """
    First-In-First-Out (FIFO) Page Replacement Algorithm.
    
    Args:
        page_ref_string: Comma-separated page references (e.g., "1,2,3,1,4")
        frame_count: Number of physical memory frames
    
    Returns:
        Dictionary with step-by-step state, hits, faults, and ratio
    """
    pages = [int(p.strip()) for p in page_ref_string.split(',') if p.strip()]
    frames = []
    steps = []
    hits = 0
    faults = 0
    queue = []  # Tracks insertion order for FIFO
    
    for i, page in enumerate(pages):
        step = {
            'step': i + 1,
            'page': page,
            'frames_before': list(frames),
            'action': '',
            'frames_after': None,
            'hit': False
        }
        
        if page in frames:
            # Page hit - already in memory
            hits += 1
            step['action'] = 'HIT'
            step['hit'] = True
            step['frames_after'] = list(frames)
        else:
            # Page fault
            faults += 1
            step['action'] = 'FAULT'
            step['hit'] = False
            
            if len(frames) < frame_count:
                # Free frame available - add page
                frames.append(page)
                queue.append(page)
            else:
                # Replace oldest page (FIFO)
                oldest = queue.pop(0)
                frames = [p if p != oldest else page for p in frames]
                queue.append(page)
            
            step['frames_after'] = list(frames)
        
        steps.append(step)
    
    total = hits + faults
    hit_ratio = hits / total if total > 0 else 0
    fault_ratio = faults / total if total > 0 else 0
    
    return {
        'algorithm': 'FIFO',
        'page_reference': page_ref_string,
        'frame_count': frame_count,
        'steps': steps,
        'hits': hits,
        'faults': faults,
        'hit_ratio': round(hit_ratio, 4),
        'fault_ratio': round(fault_ratio, 4)
    }


def simulate_lru(page_ref_string, frame_count):
    """
    Least Recently Used (LRU) Page Replacement Algorithm.
    
    Args:
        page_ref_string: Comma-separated page references
        frame_count: Number of physical memory frames
    
    Returns:
        Dictionary with step-by-step state, hits, faults, and ratio
    """
    pages = [int(p.strip()) for p in page_ref_string.split(',') if p.strip()]
    frames = []
    steps = []
    hits = 0
    faults = 0
    # OrderedDict to track LRU order (most recent at end)
    lru_tracker = OrderedDict()
    
    for i, page in enumerate(pages):
        step = {
            'step': i + 1,
            'page': page,
            'frames_before': list(frames),
            'action': '',
            'frames_after': None,
            'hit': False
        }
        
        if page in frames:
            # Page hit
            hits += 1
            step['action'] = 'HIT'
            step['hit'] = True
            # Move to end (most recently used)
            if page in lru_tracker:
                del lru_tracker[page]
            lru_tracker[page] = True
            step['frames_after'] = list(frames)
        else:
            # Page fault
            faults += 1
            step['action'] = 'FAULT'
            step['hit'] = False
            
            if len(frames) < frame_count:
                # Free frame available
                frames.append(page)
                lru_tracker[page] = True
            else:
                # Replace least recently used (first item)
                lru_page = next(iter(lru_tracker))
                del lru_tracker[lru_page]
                frames = [p if p != lru_page else page for p in frames]
                lru_tracker[page] = True
            
            step['frames_after'] = list(frames)
        
        steps.append(step)
    
    total = hits + faults
    hit_ratio = hits / total if total > 0 else 0
    fault_ratio = faults / total if total > 0 else 0
    
    return {
        'algorithm': 'LRU',
        'page_reference': page_ref_string,
        'frame_count': frame_count,
        'steps': steps,
        'hits': hits,
        'faults': faults,
        'hit_ratio': round(hit_ratio, 4),
        'fault_ratio': round(fault_ratio, 4)
    }


def simulate_lifo(page_ref_string, frame_count):
    """
    Last-In-First-Out (LIFO) Page Replacement Algorithm.
    
    Args:
        page_ref_string: Comma-separated page references
        frame_count: Number of physical memory frames
    
    Returns:
        Dictionary with step-by-step state, hits, faults, and ratio
    """
    pages = [int(p.strip()) for p in page_ref_string.split(',') if p.strip()]
    frames = []
    steps = []
    hits = 0
    faults = 0
    # Stack to track insertion order for LIFO
    stack = []
    
    for i, page in enumerate(pages):
        step = {
            'step': i + 1,
            'page': page,
            'frames_before': list(frames),
            'action': '',
            'frames_after': None,
            'hit': False
        }
        
        if page in frames:
            # Page hit
            hits += 1
            step['action'] = 'HIT'
            step['hit'] = True
            step['frames_after'] = list(frames)
        else:
            # Page fault
            faults += 1
            step['action'] = 'FAULT'
            step['hit'] = False
            
            if len(frames) < frame_count:
                # Free frame available
                frames.append(page)
                stack.append(page)
            else:
                # Replace most recently added (LIFO)
                lifo_page = stack.pop()
                frames = [p if p != lifo_page else page for p in frames]
                stack.append(page)
            
            step['frames_after'] = list(frames)
        
        steps.append(step)
    
    total = hits + faults
    hit_ratio = hits / total if total > 0 else 0
    fault_ratio = faults / total if total > 0 else 0
    
    return {
        'algorithm': 'LIFO',
        'page_reference': page_ref_string,
        'frame_count': frame_count,
        'steps': steps,
        'hits': hits,
        'faults': faults,
        'hit_ratio': round(hit_ratio, 4),
        'fault_ratio': round(fault_ratio, 4)
    }


def simulate_optimal(page_ref_string, frame_count):
    """
    Optimal Page Replacement Algorithm.
    
    Uses future knowledge to replace the page that won't be used for longest time.
    
    Args:
        page_ref_string: Comma-separated page references
        frame_count: Number of physical memory frames
    
    Returns:
        Dictionary with step-by-step state, hits, faults, and ratio
    """
    pages = [int(p.strip()) for p in page_ref_string.split(',') if p.strip()]
    frames = []
    steps = []
    hits = 0
    faults = 0
    
    for i, page in enumerate(pages):
        step = {
            'step': i + 1,
            'page': page,
            'frames_before': list(frames),
            'action': '',
            'frames_after': None,
            'hit': False
        }
        
        if page in frames:
            # Page hit
            hits += 1
            step['action'] = 'HIT'
            step['hit'] = True
            step['frames_after'] = list(frames)
        else:
            # Page fault
            faults += 1
            step['action'] = 'FAULT'
            step['hit'] = False
            
            if len(frames) < frame_count:
                # Free frame available
                frames.append(page)
            else:
                # Find page to replace (the one used furthest in future)
                future_uses = {}
                for f in frames:
                    # Find next use of this frame's page
                    try:
                        next_use = pages[i + 1:].index(f)
                        future_uses[f] = next_use
                    except ValueError:
                        # Page never used again
                        future_uses[f] = float('inf')
                
                # Replace page with furthest future use
                page_to_replace = max(future_uses, key=future_uses.get)
                frames = [p if p != page_to_replace else page for p in frames]
            
            step['frames_after'] = list(frames)
        
        steps.append(step)
    
    total = hits + faults
    hit_ratio = hits / total if total > 0 else 0
    fault_ratio = faults / total if total > 0 else 0
    
    return {
        'algorithm': 'Optimal',
        'page_reference': page_ref_string,
        'frame_count': frame_count,
        'steps': steps,
        'hits': hits,
        'faults': faults,
        'hit_ratio': round(hit_ratio, 4),
        'fault_ratio': round(fault_ratio, 4)
    }


# =============================================================================
# MEMORY ALLOCATION ALGORITHMS
# =============================================================================

def simulate_first_fit(memory_blocks, process_sizes):
    """
    First Fit Memory Allocation Algorithm.
    
    Allocates the first block that's large enough.
    
    Args:
        memory_blocks: Comma-separated block sizes (e.g., "100,200,50,300")
        process_sizes: Comma-separated process sizes (e.g., "50,100,200")
    
    Returns:
        Dictionary with allocation map, internal fragmentation, external fragmentation
    """
    blocks = [int(b.strip()) for b in memory_blocks.split(',') if b.strip()]
    processes = [int(p.strip()) for p in process_sizes.split(',') if p.strip()]
    
    allocation = []
    block_status = [{'id': i + 1, 'size': b, 'allocated_to': None, 'internal_frag': 0} for i, b in enumerate(blocks)]
    total_internal_frag = 0
    total_external_frag = 0
    
    for i, process in enumerate(processes):
        allocated = False
        for j, block in enumerate(block_status):
            if block['allocated_to'] is None and block['size'] >= process:
                # Allocate to this block
                internal_frag = block['size'] - process
                block_status[j]['allocated_to'] = f'P{i + 1}'
                block_status[j]['internal_frag'] = internal_frag
                total_internal_frag += internal_frag
                allocation.append({
                    'process': f'P{i + 1}',
                    'process_size': process,
                    'block': block['id'],
                    'block_size': block['size'],
                    'internal_fragmentation': internal_frag
                })
                allocated = True
                break
        
        if not allocated:
            # Process could not be allocated
            allocation.append({
                'process': f'P{i + 1}',
                'process_size': process,
                'block': None,
                'block_size': None,
                'internal_fragmentation': None,
                'status': 'NOT ALLOCATED'
            })
            total_external_frag += process
    
    # Calculate external fragmentation (sum of unallocated blocks)
    for block in block_status:
        if block['allocated_to'] is None:
            total_external_frag += block['size']
    
    return {
        'algorithm': 'First Fit',
        'memory_blocks': memory_blocks,
        'process_sizes': process_sizes,
        'allocation': allocation,
        'block_status': block_status,
        'total_internal_fragmentation': total_internal_frag,
        'total_external_fragmentation': total_external_frag
    }


def simulate_best_fit(memory_blocks, process_sizes):
    """
    Best Fit Memory Allocation Algorithm.
    
    Allocates the smallest block that's large enough (minimizes wasted space).
    
    Args:
        memory_blocks: Comma-separated block sizes
        process_sizes: Comma-separated process sizes
    
    Returns:
        Dictionary with allocation map, internal fragmentation, external fragmentation
    """
    blocks = [int(b.strip()) for b in memory_blocks.split(',') if b.strip()]
    processes = [int(p.strip()) for p in process_sizes.split(',') if p.strip()]
    
    allocation = []
    block_status = [{'id': i + 1, 'size': b, 'allocated_to': None, 'internal_frag': 0} for i, b in enumerate(blocks)]
    total_internal_frag = 0
    total_external_frag = 0
    
    for i, process in enumerate(processes):
        allocated = False
        # Find all fitting blocks and choose the smallest
        fitting_blocks = [(j, b['size']) for j, b in enumerate(block_status) 
                         if b['allocated_to'] is None and b['size'] >= process]
        
        if fitting_blocks:
            # Choose the smallest fitting block
            best_idx = min(fitting_blocks, key=lambda x: x[1])[0]
            block = block_status[best_idx]
            internal_frag = block['size'] - process
            block_status[best_idx]['allocated_to'] = f'P{i + 1}'
            block_status[best_idx]['internal_frag'] = internal_frag
            total_internal_frag += internal_frag
            allocation.append({
                'process': f'P{i + 1}',
                'process_size': process,
                'block': block['id'],
                'block_size': block['size'],
                'internal_fragmentation': internal_frag
            })
            allocated = True
        
        if not allocated:
            allocation.append({
                'process': f'P{i + 1}',
                'process_size': process,
                'block': None,
                'block_size': None,
                'internal_fragmentation': None,
                'status': 'NOT ALLOCATED'
            })
            total_external_frag += process
    
    # Calculate external fragmentation
    for block in block_status:
        if block['allocated_to'] is None:
            total_external_frag += block['size']
    
    return {
        'algorithm': 'Best Fit',
        'memory_blocks': memory_blocks,
        'process_sizes': process_sizes,
        'allocation': allocation,
        'block_status': block_status,
        'total_internal_fragmentation': total_internal_frag,
        'total_external_fragmentation': total_external_frag
    }


def simulate_worst_fit(memory_blocks, process_sizes):
    """
    Worst Fit Memory Allocation Algorithm.
    
    Allocates the largest block available (leaves largest remaining hole).
    
    Args:
        memory_blocks: Comma-separated block sizes
        process_sizes: Comma-separated process sizes
    
    Returns:
        Dictionary with allocation map, internal fragmentation, external fragmentation
    """
    blocks = [int(b.strip()) for b in memory_blocks.split(',') if b.strip()]
    processes = [int(p.strip()) for p in process_sizes.split(',') if p.strip()]
    
    allocation = []
    block_status = [{'id': i + 1, 'size': b, 'allocated_to': None, 'internal_frag': 0} for i, b in enumerate(blocks)]
    total_internal_frag = 0
    total_external_frag = 0
    
    for i, process in enumerate(processes):
        allocated = False
        # Find all fitting blocks and choose the largest
        fitting_blocks = [(j, b['size']) for j, b in enumerate(block_status) 
                         if b['allocated_to'] is None and b['size'] >= process]
        
        if fitting_blocks:
            # Choose the largest fitting block
            worst_idx = max(fitting_blocks, key=lambda x: x[1])[0]
            block = block_status[worst_idx]
            internal_frag = block['size'] - process
            block_status[worst_idx]['allocated_to'] = f'P{i + 1}'
            block_status[worst_idx]['internal_frag'] = internal_frag
            total_internal_frag += internal_frag
            allocation.append({
                'process': f'P{i + 1}',
                'process_size': process,
                'block': block['id'],
                'block_size': block['size'],
                'internal_fragmentation': internal_frag
            })
            allocated = True
        
        if not allocated:
            allocation.append({
                'process': f'P{i + 1}',
                'process_size': process,
                'block': None,
                'block_size': None,
                'internal_fragmentation': None,
                'status': 'NOT ALLOCATED'
            })
            total_external_frag += process
    
    # Calculate external fragmentation
    for block in block_status:
        if block['allocated_to'] is None:
            total_external_frag += block['size']
    
    return {
        'algorithm': 'Worst Fit',
        'memory_blocks': memory_blocks,
        'process_sizes': process_sizes,
        'allocation': allocation,
        'block_status': block_status,
        'total_internal_fragmentation': total_internal_frag,
        'total_external_fragmentation': total_external_frag
    }


def simulate_next_fit(memory_blocks, process_sizes):
    """
    Next Fit Memory Allocation Algorithm.
    
    Starts searching from where last allocation ended.
    
    Args:
        memory_blocks: Comma-separated block sizes
        process_sizes: Comma-separated process sizes
    
    Returns:
        Dictionary with allocation map, internal fragmentation, external fragmentation
    """
    blocks = [int(b.strip()) for b in memory_blocks.split(',') if b.strip()]
    processes = [int(p.strip()) for p in process_sizes.split(',') if p.strip()]
    
    allocation = []
    block_status = [{'id': i + 1, 'size': b, 'allocated_to': None, 'internal_frag': 0} for i, b in enumerate(blocks)]
    total_internal_frag = 0
    total_external_frag = 0
    
    # Start searching from beginning
    last_allocated_idx = -1
    
    for i, process in enumerate(processes):
        allocated = False
        n = len(block_status)
        
        # Search from last position + 1, wrapping around
        for offset in range(n):
            idx = (last_allocated_idx + 1 + offset) % n
            block = block_status[idx]
            
            if block['allocated_to'] is None and block['size'] >= process:
                internal_frag = block['size'] - process
                block_status[idx]['allocated_to'] = f'P{i + 1}'
                block_status[idx]['internal_frag'] = internal_frag
                total_internal_frag += internal_frag
                last_allocated_idx = idx
                allocation.append({
                    'process': f'P{i + 1}',
                    'process_size': process,
                    'block': block['id'],
                    'block_size': block['size'],
                    'internal_fragmentation': internal_frag
                })
                allocated = True
                break
        
        if not allocated:
            allocation.append({
                'process': f'P{i + 1}',
                'process_size': process,
                'block': None,
                'block_size': None,
                'internal_fragmentation': None,
                'status': 'NOT ALLOCATED'
            })
            total_external_frag += process
    
    # Calculate external fragmentation
    for block in block_status:
        if block['allocated_to'] is None:
            total_external_frag += block['size']
    
    return {
        'algorithm': 'Next Fit',
        'memory_blocks': memory_blocks,
        'process_sizes': process_sizes,
        'allocation': allocation,
        'block_status': block_status,
        'total_internal_fragmentation': total_internal_frag,
        'total_external_fragmentation': total_external_frag
    }


# =============================================================================
# FLASK API ROUTES
# =============================================================================

@app.route('/api/paging', methods=['POST'])
def api_paging():
    """
    API Endpoint for Demand Paging Simulation.
    
    Accepts JSON:
    {
        "algorithm": "FIFO|LRU|LIFO|Optimal",
        "page_reference": "1,2,3,4,1,2",
        "frame_count": 3
    }
    
    Returns JSON with step-by-step simulation results.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        algorithm = data.get('algorithm', '').upper()
        page_reference = data.get('page_reference', '')
        frame_count = data.get('frame_count', 3)
        
        # Validation
        if not page_reference:
            return jsonify({'error': 'Page reference string is required'}), 400
        
        if frame_count < 1:
            return jsonify({'error': 'Frame count must be at least 1'}), 400
        
        # Route to appropriate algorithm
        if algorithm == 'FIFO':
            result = simulate_fifo(page_reference, frame_count)
        elif algorithm == 'LRU':
            result = simulate_lru(page_reference, frame_count)
        elif algorithm == 'LIFO':
            result = simulate_lifo(page_reference, frame_count)
        elif algorithm == 'OPTIMAL':
            result = simulate_optimal(page_reference, frame_count)
        else:
            return jsonify({'error': f'Unknown algorithm: {algorithm}. Use FIFO, LRU, LIFO, or Optimal'}), 400
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/allocation', methods=['POST'])
def api_allocation():
    """
    API Endpoint for Memory Allocation Simulation.
    
    Accepts JSON:
    {
        "algorithm": "First Fit|Best Fit|Worst Fit|Next Fit",
        "memory_blocks": "100,200,50,300",
        "process_sizes": "50,100,200"
    }
    
    Returns JSON with allocation map and fragmentation calculations.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        algorithm = data.get('algorithm', '').lower().replace(' ', '')
        memory_blocks = data.get('memory_blocks', '')
        process_sizes = data.get('process_sizes', '')
        
        # Validation
        if not memory_blocks:
            return jsonify({'error': 'Memory blocks are required'}), 400
        
        if not process_sizes:
            return jsonify({'error': 'Process sizes are required'}), 400
        
        # Route to appropriate algorithm
        if algorithm in ['firstfit', 'first_fit']:
            result = simulate_first_fit(memory_blocks, process_sizes)
        elif algorithm in ['bestfit', 'best_fit']:
            result = simulate_best_fit(memory_blocks, process_sizes)
        elif algorithm in ['worstfit', 'worst_fit']:
            result = simulate_worst_fit(memory_blocks, process_sizes)
        elif algorithm in ['nextfit', 'next_fit']:
            result = simulate_next_fit(memory_blocks, process_sizes)
        else:
            return jsonify({'error': f'Unknown algorithm: {algorithm}. Use First Fit, Best Fit, Worst Fit, or Next Fit'}), 400
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'Virtual Memory Optimizer'}), 200


# =============================================================================
# STATIC FILE SERVING (SPA)
# =============================================================================

@app.route('/')
def serve_index():
    """Serve the main HTML file."""
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images)."""
    return send_from_directory(BASE_DIR, filename)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)