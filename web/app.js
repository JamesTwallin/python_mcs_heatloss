// MCS Heat Loss Calculator Web App
let pyodide = null;
let projectData = {
    building_name: 'My House',
    postcode_area: 'M',
    building_category: 'B',
    external_temp: -3.1,
    rooms: []
};

let currentEditingRoomIndex = null;

// Initialize Pyodide and load Python code
async function initPyodide() {
    setStatus('Loading Python environment...', 'loading');
    try {
        pyodide = await loadPyodide();

        // Load the mcs_calculator Python module
        await pyodide.runPythonAsync(`
            import sys
            import json
            from js import fetch

            # Fetch and load the Python modules
            # We'll embed the Python code directly for simplicity
        `);

        setStatus('Ready', 'success');
        updateLocationInfo();
    } catch (error) {
        setStatus('Error loading Python: ' + error.message, 'error');
        console.error(error);
    }
}

// Set status message
function setStatus(message, type) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.className = 'status ' + type;
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            statusEl.textContent = '';
            statusEl.className = 'status';
        }, 3000);
    }
}

// Update location info
async function updateLocationInfo() {
    const postcodeArea = document.getElementById('postcodeArea').value.toUpperCase();

    if (!pyodide) return;

    try {
        const result = await pyodide.runPythonAsync(`
import sys
sys.path.append('/mcs_calculator')

# Embedded degree days data (subset for demo)
degree_days_data = {
    'M': {'temp': -3.1, 'degree_days': 2275, 'location': 'North Western (Ringway)'},
    'SW': {'temp': -2.0, 'degree_days': 2033, 'location': 'Thames Valley (Heathrow)'},
    'EH': {'temp': -3.2, 'degree_days': 2332, 'location': 'East Scotland (Turnhouse)'},
    'G': {'temp': -3.3, 'degree_days': 2401, 'location': 'West Scotland (West Freugh)'},
    'B': {'temp': -3.3, 'degree_days': 2265, 'location': 'Severn Valley (Birmingham)'},
}

postcode = '${postcodeArea}'
if postcode in degree_days_data:
    data = degree_days_data[postcode]
    json.dumps({
        'location': data['location'],
        'design_temp': data['temp'],
        'degree_days': data['degree_days']
    })
else:
    json.dumps({'error': 'Unknown postcode area'})
        `);

        const info = JSON.parse(result);
        const infoPanel = document.getElementById('locationInfo');

        if (info.error) {
            infoPanel.innerHTML = `<p style="color: #dc3545;">${info.error}</p>`;
        } else {
            infoPanel.innerHTML = `
                <strong>Location:</strong> ${info.location}<br>
                <strong>Design Temperature:</strong> ${info.design_temp}°C<br>
                <strong>Degree Days:</strong> ${info.degree_days}
            `;
            document.getElementById('externalTemp').value = info.design_temp;
        }
    } catch (error) {
        console.error('Error updating location info:', error);
    }
}

// Render rooms list
function renderRooms() {
    const roomsList = document.getElementById('roomsList');

    if (projectData.rooms.length === 0) {
        roomsList.innerHTML = '<p class="placeholder">No rooms added yet. Click "Add Room" to get started.</p>';
        return;
    }

    roomsList.innerHTML = projectData.rooms.map((room, index) => `
        <div class="room-card">
            <div class="room-header">
                <h3>${room.name} (${room.room_type})</h3>
                <div class="room-actions">
                    <button class="btn btn-small" onclick="editRoom(${index})">Edit</button>
                    <button class="btn btn-danger btn-small" onclick="deleteRoom(${index})">Delete</button>
                </div>
            </div>
            <div class="room-details">
                <div class="room-detail">
                    <strong>Floor Area</strong>
                    <span>${room.floor_area} m²</span>
                </div>
                <div class="room-detail">
                    <strong>Height</strong>
                    <span>${room.height} m</span>
                </div>
                <div class="room-detail">
                    <strong>Design Temp</strong>
                    <span>${room.design_temp || 'Default'}°C</span>
                </div>
                <div class="room-detail">
                    <strong>ACH</strong>
                    <span>${room.air_change_rate || 'Default'}</span>
                </div>
                <div class="room-detail">
                    <strong>Fabric Elements</strong>
                    <span>${(room.walls?.length || 0) + (room.windows?.length || 0) + (room.floors?.length || 0)} items</span>
                </div>
            </div>
        </div>
    `).join('');
}

// Modal functions
function showRoomModal(editIndex = null) {
    currentEditingRoomIndex = editIndex;
    const modal = document.getElementById('roomModal');
    const title = document.getElementById('modalTitle');

    if (editIndex !== null) {
        title.textContent = 'Edit Room';
        const room = projectData.rooms[editIndex];

        document.getElementById('roomName').value = room.name;
        document.getElementById('roomType').value = room.room_type;
        document.getElementById('floorArea').value = room.floor_area;
        document.getElementById('height').value = room.height;
        document.getElementById('designTemp').value = room.design_temp || '';
        document.getElementById('airChangeRate').value = room.air_change_rate || '';

        // Load fabric elements
        renderFabricElements('walls', room.walls || []);
        renderFabricElements('windows', room.windows || []);
        renderFabricElements('floors', room.floors || []);
    } else {
        title.textContent = 'Add Room';
        document.getElementById('roomName').value = '';
        document.getElementById('roomType').value = 'Lounge';
        document.getElementById('floorArea').value = '20';
        document.getElementById('height').value = '2.4';
        document.getElementById('designTemp').value = '';
        document.getElementById('airChangeRate').value = '';

        renderFabricElements('walls', []);
        renderFabricElements('windows', []);
        renderFabricElements('floors', []);
    }

    modal.classList.add('active');
}

function closeRoomModal() {
    document.getElementById('roomModal').classList.remove('active');
}

function renderFabricElements(type, elements) {
    const container = document.getElementById(`${type}List`);
    container.innerHTML = elements.map((el, i) => createFabricElementHTML(type, el, i)).join('');
}

function createFabricElementHTML(type, element, index) {
    const commonFields = `
        <input type="text" placeholder="Name" value="${element.name || ''}"
               onchange="updateFabricElement('${type}', ${index}, 'name', this.value)">
        <input type="number" placeholder="Area (m²)" value="${element.area || ''}" step="0.1"
               onchange="updateFabricElement('${type}', ${index}, 'area', parseFloat(this.value))">
        <input type="number" placeholder="U-value (W/m²K)" value="${element.u_value || ''}" step="0.01"
               onchange="updateFabricElement('${type}', ${index}, 'u_value', parseFloat(this.value))">
    `;

    let extraFields = '';
    if (type === 'walls' || type === 'floors') {
        extraFields = `
            <input type="number" placeholder="Temp Factor (0-1)" value="${element.temperature_factor || 1}" step="0.1" min="0" max="1"
                   onchange="updateFabricElement('${type}', ${index}, 'temperature_factor', parseFloat(this.value))">
        `;
    }

    return `
        <div class="fabric-element">
            <div class="fabric-element-header">
                <span><strong>${type === 'walls' ? 'Wall' : type === 'windows' ? 'Window' : 'Floor'} ${index + 1}</strong></span>
                <button type="button" class="btn btn-danger btn-small" onclick="removeFabricElement('${type}', ${index})">Remove</button>
            </div>
            <div class="fabric-inputs">
                ${commonFields}
                ${extraFields}
            </div>
        </div>
    `;
}

// Fabric element management
let tempFabricData = { walls: [], windows: [], floors: [] };

function addFabricElement(type) {
    const newElement = {
        name: '',
        area: 0,
        u_value: 0,
        ...(type !== 'windows' && { temperature_factor: 1 })
    };

    if (!tempFabricData[type]) tempFabricData[type] = [];
    tempFabricData[type].push(newElement);
    renderFabricElements(type, tempFabricData[type]);
}

function updateFabricElement(type, index, field, value) {
    if (!tempFabricData[type]) tempFabricData[type] = [];
    if (!tempFabricData[type][index]) tempFabricData[type][index] = {};
    tempFabricData[type][index][field] = value;
}

function removeFabricElement(type, index) {
    tempFabricData[type].splice(index, 1);
    renderFabricElements(type, tempFabricData[type]);
}

function saveRoom() {
    const room = {
        name: document.getElementById('roomName').value,
        room_type: document.getElementById('roomType').value,
        floor_area: parseFloat(document.getElementById('floorArea').value),
        height: parseFloat(document.getElementById('height').value),
        design_temp: document.getElementById('designTemp').value ? parseFloat(document.getElementById('designTemp').value) : null,
        air_change_rate: document.getElementById('airChangeRate').value ? parseFloat(document.getElementById('airChangeRate').value) : null,
        walls: tempFabricData.walls || [],
        windows: tempFabricData.windows || [],
        floors: tempFabricData.floors || []
    };

    if (currentEditingRoomIndex !== null) {
        projectData.rooms[currentEditingRoomIndex] = room;
    } else {
        projectData.rooms.push(room);
    }

    renderRooms();
    closeRoomModal();
    setStatus('Room saved', 'success');
}

function editRoom(index) {
    const room = projectData.rooms[index];
    tempFabricData = {
        walls: [...(room.walls || [])],
        windows: [...(room.windows || [])],
        floors: [...(room.floors || [])]
    };
    showRoomModal(index);
}

function deleteRoom(index) {
    if (confirm('Are you sure you want to delete this room?')) {
        projectData.rooms.splice(index, 1);
        renderRooms();
        setStatus('Room deleted', 'success');
    }
}

// Calculate heat loss
async function calculateHeatLoss() {
    if (!pyodide) {
        setStatus('Python not loaded yet', 'error');
        return;
    }

    if (projectData.rooms.length === 0) {
        setStatus('Please add at least one room', 'error');
        return;
    }

    setStatus('Calculating...', 'loading');

    // Update project data from form
    projectData.building_name = document.getElementById('buildingName').value;
    projectData.postcode_area = document.getElementById('postcodeArea').value.toUpperCase();
    projectData.building_category = document.getElementById('buildingCategory').value;
    projectData.external_temp = parseFloat(document.getElementById('externalTemp').value);

    try {
        // Pass data to Python and calculate
        pyodide.globals.set('project_json', JSON.stringify(projectData));

        const result = await pyodide.runPythonAsync(`
import json

# Parse project data
project = json.loads(project_json)

# Simple calculation (we'll embed simplified logic)
results = {
    'building_name': project['building_name'],
    'total_heat_loss_watts': 0,
    'total_heat_loss_kw': 0,
    'rooms': []
}

# Simplified calculation for each room
for room in project['rooms']:
    volume = room['floor_area'] * room['height']
    external_temp = project['external_temp']
    design_temp = room['design_temp'] if room['design_temp'] else 21

    # ACH defaults by category and room type
    ach_defaults = {
        'A': {'Lounge': 1.5, 'Kitchen': 2.0, 'Bedroom': 1.0, 'Bathroom': 3.0},
        'B': {'Lounge': 1.0, 'Kitchen': 1.5, 'Bedroom': 1.0, 'Bathroom': 1.5},
        'C': {'Lounge': 0.5, 'Kitchen': 1.5, 'Bedroom': 0.5, 'Bathroom': 1.5}
    }
    category = project['building_category']
    ach = room['air_change_rate'] if room['air_change_rate'] else ach_defaults.get(category, {}).get(room['room_type'], 1.0)

    # Calculate fabric loss
    fabric_loss = 0
    for wall in room.get('walls', []):
        temp_diff = design_temp - external_temp
        fabric_loss += wall['area'] * wall['u_value'] * temp_diff * wall.get('temperature_factor', 1.0)

    for window in room.get('windows', []):
        temp_diff = design_temp - external_temp
        fabric_loss += window['area'] * window['u_value'] * temp_diff

    for floor in room.get('floors', []):
        temp_diff = design_temp - external_temp
        fabric_loss += floor['area'] * floor['u_value'] * temp_diff * floor.get('temperature_factor', 0.5)

    # Calculate ventilation loss: Q = 0.33 × n × V × ΔT
    temp_diff = design_temp - external_temp
    vent_loss = 0.33 * ach * volume * temp_diff

    total_room_loss = fabric_loss + vent_loss

    results['rooms'].append({
        'name': room['name'],
        'design_temp': design_temp,
        'fabric_loss': round(fabric_loss, 1),
        'ventilation_loss': round(vent_loss, 1),
        'total_loss': round(total_room_loss, 1)
    })

    results['total_heat_loss_watts'] += total_room_loss

results['total_heat_loss_kw'] = round(results['total_heat_loss_watts'] / 1000, 2)
results['total_heat_loss_watts'] = round(results['total_heat_loss_watts'], 1)

json.dumps(results)
        `);

        const results = JSON.parse(result);
        displayResults(results);
        setStatus('Calculation complete', 'success');
    } catch (error) {
        setStatus('Calculation error: ' + error.message, 'error');
        console.error(error);
    }
}

function displayResults(results) {
    const resultsDiv = document.getElementById('results');

    const summaryHTML = `
        <div class="results-summary">
            <div class="result-card">
                <h3>Total Heat Loss</h3>
                <div class="value">${results.total_heat_loss_kw}</div>
                <div class="unit">kW</div>
            </div>
            <div class="result-card">
                <h3>Total Heat Loss</h3>
                <div class="value">${results.total_heat_loss_watts}</div>
                <div class="unit">Watts</div>
            </div>
            <div class="result-card">
                <h3>Number of Rooms</h3>
                <div class="value">${results.rooms.length}</div>
                <div class="unit">rooms</div>
            </div>
        </div>
    `;

    const roomsTableHTML = `
        <div class="room-results">
            <h3>Room-by-Room Breakdown</h3>
            <div class="room-result-row header">
                <div>Room</div>
                <div>Design Temp</div>
                <div>Fabric Loss</div>
                <div>Vent Loss</div>
                <div>Total Loss</div>
            </div>
            ${results.rooms.map(room => `
                <div class="room-result-row">
                    <div>${room.name}</div>
                    <div>${room.design_temp}°C</div>
                    <div>${room.fabric_loss}W</div>
                    <div>${room.ventilation_loss}W</div>
                    <div><strong>${room.total_loss}W</strong></div>
                </div>
            `).join('')}
        </div>
    `;

    resultsDiv.innerHTML = summaryHTML + roomsTableHTML;
}

// JSON load/save
function saveJSON() {
    projectData.building_name = document.getElementById('buildingName').value;
    projectData.postcode_area = document.getElementById('postcodeArea').value.toUpperCase();
    projectData.building_category = document.getElementById('buildingCategory').value;
    projectData.external_temp = parseFloat(document.getElementById('externalTemp').value);

    const json = JSON.stringify(projectData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectData.building_name.replace(/\s+/g, '_')}_heat_loss.json`;
    a.click();
    URL.revokeObjectURL(url);

    setStatus('JSON saved', 'success');
}

function loadJSON() {
    document.getElementById('fileInput').click();
}

function handleFileLoad(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            projectData = JSON.parse(e.target.result);

            document.getElementById('buildingName').value = projectData.building_name;
            document.getElementById('postcodeArea').value = projectData.postcode_area;
            document.getElementById('buildingCategory').value = projectData.building_category;
            document.getElementById('externalTemp').value = projectData.external_temp;

            renderRooms();
            updateLocationInfo();
            setStatus('Project loaded', 'success');
        } catch (error) {
            setStatus('Error loading JSON: ' + error.message, 'error');
        }
    };
    reader.readAsText(file);
}

function newProject() {
    if (projectData.rooms.length > 0 && !confirm('This will clear all current data. Continue?')) {
        return;
    }

    projectData = {
        building_name: 'My House',
        postcode_area: 'M',
        building_category: 'B',
        external_temp: -3.1,
        rooms: []
    };

    document.getElementById('buildingName').value = projectData.building_name;
    document.getElementById('postcodeArea').value = projectData.postcode_area;
    document.getElementById('buildingCategory').value = projectData.building_category;
    document.getElementById('externalTemp').value = projectData.external_temp;
    document.getElementById('results').innerHTML = '<p class="placeholder">Click "Calculate Heat Loss" to see results</p>';

    renderRooms();
    updateLocationInfo();
    setStatus('New project created', 'success');
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Pyodide
    initPyodide();

    // Toolbar buttons
    document.getElementById('newProject').addEventListener('click', newProject);
    document.getElementById('loadJson').addEventListener('click', loadJSON);
    document.getElementById('saveJson').addEventListener('click', saveJSON);
    document.getElementById('fileInput').addEventListener('change', handleFileLoad);

    // Building config
    document.getElementById('postcodeArea').addEventListener('change', updateLocationInfo);

    // Room buttons
    document.getElementById('addRoom').addEventListener('click', () => {
        tempFabricData = { walls: [], windows: [], floors: [] };
        showRoomModal();
    });

    // Modal buttons
    document.querySelector('.close').addEventListener('click', closeRoomModal);
    document.getElementById('cancelRoom').addEventListener('click', closeRoomModal);
    document.getElementById('saveRoom').addEventListener('click', saveRoom);

    // Fabric element buttons
    document.getElementById('addWall').addEventListener('click', () => addFabricElement('walls'));
    document.getElementById('addWindow').addEventListener('click', () => addFabricElement('windows'));
    document.getElementById('addFloor').addEventListener('click', () => addFabricElement('floors'));

    // Calculate button
    document.getElementById('calculate').addEventListener('click', calculateHeatLoss);

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('roomModal');
        if (event.target === modal) {
            closeRoomModal();
        }
    });

    // Initial render
    renderRooms();
});
