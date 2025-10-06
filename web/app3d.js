// 3D Heat Loss Calculator Application
// Uses Three.js for 3D visualization and Pyodide for calculations

let scene, camera, renderer, controls;
let raycaster, mouse;
let grid, gridHelper;
let rooms = [];
let selectedRoom = null;
let currentMode = 'select';
let showHeatmap = true;
let showLabels = true;

// Project data
let projectData = {
    building_name: 'My House',
    postcode_area: 'M',
    building_category: 'B',
    external_temp: -3.1,
    rooms: []
};

// Building shell data
let buildingShell = null;

// Initialize lighting
function initLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    scene.add(directionalLight);
}

// Initialize grid and ground
function initGrid() {
    gridHelper = new THREE.GridHelper(50, 50, 0x444444, 0x222222);
    scene.add(gridHelper);

    // Ground plane (for shadows)
    const groundGeometry = new THREE.PlaneGeometry(100, 100);
    const groundMaterial = new THREE.ShadowMaterial({ opacity: 0.3 });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);
}

// Initialize Three.js Scene
function initThree() {
    const canvas = document.getElementById('threeCanvas');
    const container = document.getElementById('canvas-container');

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x16213e);
    scene.fog = new THREE.Fog(0x16213e, 50, 200);

    // Camera
    camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(15, 15, 15);
    camera.lookAt(0, 0, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        antialias: true,
        alpha: true
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.setClearColor(0x16213e, 1.0);

    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 5;
    controls.maxDistance = 100;
    controls.maxPolarAngle = Math.PI / 2 - 0.1;

    initLighting();
    initGrid();

    // Raycaster for mouse picking
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    // Event listeners
    window.addEventListener('resize', onWindowResize, false);
    canvas.addEventListener('mousemove', onMouseMove, false);
    canvas.addEventListener('click', onClick, false);

    // Start animation loop
    animate();

    setStatus('3D View Ready');
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// Window resize handler
function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// Mouse move handler
function onMouseMove(event) {
    const canvas = document.getElementById('threeCanvas');
    const rect = canvas.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    // Update coordinates display
    const coords = document.getElementById('coordinates');
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        const point = intersects[0].point;
        coords.textContent = `X: ${point.x.toFixed(2)} Y: ${point.y.toFixed(2)} Z: ${point.z.toFixed(2)}`;
    }
}

// Click handler
function onClick(event) {
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);

    if (intersects.length > 0) {
        const object = intersects[0].object;

        // Find which room was clicked
        for (let room of rooms) {
            if (room.mesh === object || room.mesh === object.parent) {
                selectRoom(room);
                return;
            }
        }
    }
}

// Create 3D room visualization
function createRoomMesh(roomData, index) {
    const group = new THREE.Group();
    group.userData = { roomData, index };

    const width = roomData.width || 5;
    const depth = roomData.depth || 4;
    const height = roomData.height || 2.4;

    // Position - use saved position or auto-grid
    let x, z;
    if (roomData.position_x !== undefined && roomData.position_z !== undefined) {
        x = roomData.position_x;
        z = roomData.position_z;
    } else {
        // Auto-grid layout
        const gridSize = Math.ceil(Math.sqrt(rooms.length + 1));
        x = (index % gridSize) * 8;
        z = Math.floor(index / gridSize) * 8;
        // Save the auto-calculated position
        roomData.position_x = x;
        roomData.position_z = z;
    }

    group.position.set(x, 0, z);

    // Floor
    const floorGeometry = new THREE.BoxGeometry(width, 0.1, depth);
    const floorMaterial = new THREE.MeshStandardMaterial({
        color: 0x8d6e63,
        roughness: 0.8
    });
    const floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.position.y = 0.05;
    floor.receiveShadow = true;
    group.add(floor);

    // Walls will be created with window openings
    // We'll create them after processing windows to know where to cut holes
    const wallThickness = 0.05;  // Thin walls - 5cm
    const wallMaterial = new THREE.MeshStandardMaterial({
        color: 0xeeeeee,
        roughness: 0.7,
        metalness: 0.1
    });

    // Store wall info for later (we'll create walls after windows)
    const wallsToCreate = {
        front: { position: [0, height / 2, -depth / 2], size: [width, height, wallThickness], windows: [] },
        back: { position: [0, height / 2, depth / 2], size: [width, height, wallThickness], windows: [] },
        left: { position: [-width / 2, height / 2, 0], size: [wallThickness, height, depth], windows: [] },
        right: { position: [width / 2, height / 2, 0], size: [wallThickness, height, depth], windows: [] }
    };

    // Add windows if present
    if (roomData.windows && roomData.windows.length > 0) {
        const windowGlassMaterial = new THREE.MeshStandardMaterial({
            color: 0x87CEEB,
            transparent: true,
            opacity: 0.4,
            roughness: 0.1,
            metalness: 0.1,
            side: THREE.DoubleSide
        });

        const windowFrameMaterial = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            roughness: 0.5
        });

        // Group windows by wall for even spacing
        const windowsByWall = { front: [], back: [], left: [], right: [] };
        roomData.windows.forEach((window, i) => {
            const wallType = window.wall || 'front';
            windowsByWall[wallType].push({ window, index: i });
        });

        // Render windows with even spacing per wall
        Object.entries(windowsByWall).forEach(([wallType, windowsOnWall]) => {
            windowsOnWall.forEach(({ window, index }, positionIndex) => {
                const windowWidth = Math.min(width * 0.3, 2);
                const windowHeight = Math.min(height * 0.6, 1.5);
                const numWindows = windowsOnWall.length;

                // Window with frame
                const frameThickness = 0.05;  // 5cm frame
                const frameDepth = 0.02;      // 2cm depth

                // Glass pane
                const windowGlass = new THREE.Mesh(
                    new THREE.PlaneGeometry(windowWidth - frameThickness * 2, windowHeight - frameThickness * 2),
                    windowGlassMaterial
                );
                windowGlass.renderOrder = 999;

                // Frame - 4 pieces around the glass
                const topFrame = new THREE.Mesh(
                    new THREE.BoxGeometry(windowWidth, frameThickness, frameDepth),
                    windowFrameMaterial
                );
                topFrame.position.set(0, windowHeight / 2 - frameThickness / 2, 0);

                const bottomFrame = new THREE.Mesh(
                    new THREE.BoxGeometry(windowWidth, frameThickness, frameDepth),
                    windowFrameMaterial
                );
                bottomFrame.position.set(0, -windowHeight / 2 + frameThickness / 2, 0);

                const leftFrame = new THREE.Mesh(
                    new THREE.BoxGeometry(frameThickness, windowHeight - frameThickness * 2, frameDepth),
                    windowFrameMaterial
                );
                leftFrame.position.set(-windowWidth / 2 + frameThickness / 2, 0, 0);

                const rightFrame = new THREE.Mesh(
                    new THREE.BoxGeometry(frameThickness, windowHeight - frameThickness * 2, frameDepth),
                    windowFrameMaterial
                );
                rightFrame.position.set(windowWidth / 2 - frameThickness / 2, 0, 0);

                const windowGroup = new THREE.Group();
                windowGroup.add(windowGlass);
                windowGroup.add(topFrame);
                windowGroup.add(bottomFrame);
                windowGroup.add(leftFrame);
                windowGroup.add(rightFrame);

                // Calculate even spacing along wall
                // Spread windows evenly across the wall length with padding
                let offset = 0;
                let wallLength = 0;

                switch(wallType) {
                    case 'front':
                    case 'back':
                        wallLength = width;
                        break;
                    case 'left':
                    case 'right':
                        wallLength = depth;
                        break;
                }

                if (numWindows === 1) {
                    offset = 0;  // Center
                } else {
                    // Spread across wall with padding
                    const usableLength = wallLength * 0.8;  // 80% of wall length
                    const spacing = usableLength / (numWindows - 1);
                    offset = (positionIndex * spacing) - (usableLength / 2);
                }

                const windowOffset = 0.03;  // Slight offset in front of wall

                switch(wallType) {
                    case 'front': // North wall (-Z)
                        windowGroup.rotation.y = 0;
                        windowGroup.position.set(offset, height * 0.6, -depth / 2 - windowOffset);
                        wallsToCreate.front.windows.push({ x: offset, y: height * 0.6, width: windowWidth, height: windowHeight });
                        break;
                    case 'back': // South wall (+Z)
                        windowGroup.rotation.y = Math.PI;
                        windowGroup.position.set(-offset, height * 0.6, depth / 2 + windowOffset);
                        wallsToCreate.back.windows.push({ x: -offset, y: height * 0.6, width: windowWidth, height: windowHeight });
                        break;
                    case 'left': // West wall (-X)
                        windowGroup.rotation.y = Math.PI / 2;
                        windowGroup.position.set(-width / 2 - windowOffset, height * 0.6, offset);
                        wallsToCreate.left.windows.push({ x: offset, y: height * 0.6, width: windowWidth, height: windowHeight });
                        break;
                    case 'right': // East wall (+X)
                        windowGroup.rotation.y = -Math.PI / 2;
                        windowGroup.position.set(width / 2 + windowOffset, height * 0.6, -offset);
                        wallsToCreate.right.windows.push({ x: -offset, y: height * 0.6, width: windowWidth, height: windowHeight });
                        break;
                }

                group.add(windowGroup);
            });
        });
    }

    // Create walls with window cutouts as 4 rectangles around each window
    function createWallWithOpenings(wallInfo, wallName) {
        const [wallWidth, wallHeight, wallDepth] = wallInfo.size;
        const windows = wallInfo.windows;

        if (windows.length === 0) {
            // No windows - simple solid wall
            const wall = new THREE.Mesh(
                new THREE.BoxGeometry(wallWidth, wallHeight, wallDepth),
                wallMaterial
            );
            wall.position.set(...wallInfo.position);
            wall.castShadow = true;
            return wall;
        }

        const wallGroup = new THREE.Group();
        wallGroup.position.set(...wallInfo.position);

        // For front/back walls: wallWidth=room width, wallDepth=thickness
        // For left/right walls: wallWidth=thickness, wallDepth=room depth
        const isHorizontal = (wallName === 'front' || wallName === 'back');

        windows.forEach(win => {
            const winLocalY = win.y - wallInfo.position[1];

            const wallBottom = -wallHeight / 2;
            const wallTop = wallHeight / 2;
            const winBottom = winLocalY - win.height / 2;
            const winTop = winLocalY + win.height / 2;

            if (isHorizontal) {
                // Front/Back walls: windows positioned along X axis
                const winLocalX = win.x - wallInfo.position[0];
                const wallLeft = -wallWidth / 2;
                const wallRight = wallWidth / 2;
                const winLeft = winLocalX - win.width / 2;
                const winRight = winLocalX + win.width / 2;

                // Left rectangle
                if (winLeft > wallLeft) {
                    const leftWidth = winLeft - wallLeft;
                    const leftSegment = new THREE.Mesh(
                        new THREE.BoxGeometry(leftWidth, wallHeight, wallDepth),
                        wallMaterial
                    );
                    leftSegment.position.set((wallLeft + winLeft) / 2, 0, 0);
                    leftSegment.castShadow = true;
                    wallGroup.add(leftSegment);
                }

                // Right rectangle
                if (winRight < wallRight) {
                    const rightWidth = wallRight - winRight;
                    const rightSegment = new THREE.Mesh(
                        new THREE.BoxGeometry(rightWidth, wallHeight, wallDepth),
                        wallMaterial
                    );
                    rightSegment.position.set((winRight + wallRight) / 2, 0, 0);
                    rightSegment.castShadow = true;
                    wallGroup.add(rightSegment);
                }

                // Top rectangle
                if (winTop < wallTop) {
                    const topHeight = wallTop - winTop;
                    const topSegment = new THREE.Mesh(
                        new THREE.BoxGeometry(win.width, topHeight, wallDepth),
                        wallMaterial
                    );
                    topSegment.position.set(winLocalX, (winTop + wallTop) / 2, 0);
                    topSegment.castShadow = true;
                    wallGroup.add(topSegment);
                }

                // Bottom rectangle
                if (winBottom > wallBottom) {
                    const bottomHeight = winBottom - wallBottom;
                    const bottomSegment = new THREE.Mesh(
                        new THREE.BoxGeometry(win.width, bottomHeight, wallDepth),
                        wallMaterial
                    );
                    bottomSegment.position.set(winLocalX, (wallBottom + winBottom) / 2, 0);
                    bottomSegment.castShadow = true;
                    wallGroup.add(bottomSegment);
                }
            } else {
                // Left/Right walls: windows positioned along Z axis
                // Need to create 9 segments (3x3 grid minus center window)
                const winLocalZ = win.x - wallInfo.position[2];
                const wallFront = -wallDepth / 2;
                const wallBack = wallDepth / 2;
                const winFront = winLocalZ - win.width / 2;
                const winBack = winLocalZ + win.width / 2;

                // Row 1 (bottom): 3 segments
                if (winBottom > wallBottom) {
                    const bottomHeight = winBottom - wallBottom;
                    const bottomY = (wallBottom + winBottom) / 2;

                    // Bottom-left
                    if (winFront > wallFront) {
                        const seg = new THREE.Mesh(
                            new THREE.BoxGeometry(wallWidth, bottomHeight, winFront - wallFront),
                            wallMaterial
                        );
                        seg.position.set(0, bottomY, (wallFront + winFront) / 2);
                        seg.castShadow = true;
                        wallGroup.add(seg);
                    }

                    // Bottom-center (directly below window)
                    const seg = new THREE.Mesh(
                        new THREE.BoxGeometry(wallWidth, bottomHeight, win.width),
                        wallMaterial
                    );
                    seg.position.set(0, bottomY, winLocalZ);
                    seg.castShadow = true;
                    wallGroup.add(seg);

                    // Bottom-right
                    if (winBack < wallBack) {
                        const seg = new THREE.Mesh(
                            new THREE.BoxGeometry(wallWidth, bottomHeight, wallBack - winBack),
                            wallMaterial
                        );
                        seg.position.set(0, bottomY, (winBack + wallBack) / 2);
                        seg.castShadow = true;
                        wallGroup.add(seg);
                    }
                }

                // Row 2 (middle): only left and right segments (window is in center)
                const middleHeight = win.height;
                const middleY = winLocalY;

                // Middle-left
                if (winFront > wallFront) {
                    const seg = new THREE.Mesh(
                        new THREE.BoxGeometry(wallWidth, middleHeight, winFront - wallFront),
                        wallMaterial
                    );
                    seg.position.set(0, middleY, (wallFront + winFront) / 2);
                    seg.castShadow = true;
                    wallGroup.add(seg);
                }

                // Middle-right
                if (winBack < wallBack) {
                    const seg = new THREE.Mesh(
                        new THREE.BoxGeometry(wallWidth, middleHeight, wallBack - winBack),
                        wallMaterial
                    );
                    seg.position.set(0, middleY, (winBack + wallBack) / 2);
                    seg.castShadow = true;
                    wallGroup.add(seg);
                }

                // Row 3 (top): 3 segments
                if (winTop < wallTop) {
                    const topHeight = wallTop - winTop;
                    const topY = (winTop + wallTop) / 2;

                    // Top-left
                    if (winFront > wallFront) {
                        const seg = new THREE.Mesh(
                            new THREE.BoxGeometry(wallWidth, topHeight, winFront - wallFront),
                            wallMaterial
                        );
                        seg.position.set(0, topY, (wallFront + winFront) / 2);
                        seg.castShadow = true;
                        wallGroup.add(seg);
                    }

                    // Top-center (directly above window)
                    const seg = new THREE.Mesh(
                        new THREE.BoxGeometry(wallWidth, topHeight, win.width),
                        wallMaterial
                    );
                    seg.position.set(0, topY, winLocalZ);
                    seg.castShadow = true;
                    wallGroup.add(seg);

                    // Top-right
                    if (winBack < wallBack) {
                        const seg = new THREE.Mesh(
                            new THREE.BoxGeometry(wallWidth, topHeight, wallBack - winBack),
                            wallMaterial
                        );
                        seg.position.set(0, topY, (winBack + wallBack) / 2);
                        seg.castShadow = true;
                        wallGroup.add(seg);
                    }
                }
            }
        });

        return wallGroup;
    }

    // Add walls with openings
    group.add(createWallWithOpenings(wallsToCreate.front, 'front'));
    group.add(createWallWithOpenings(wallsToCreate.back, 'back'));
    group.add(createWallWithOpenings(wallsToCreate.left, 'left'));
    group.add(createWallWithOpenings(wallsToCreate.right, 'right'));

    // Room label
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 512;
    canvas.height = 128;
    context.fillStyle = 'rgba(255, 255, 255, 0.9)';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.font = 'bold 48px Arial';
    context.fillStyle = 'black';
    context.textAlign = 'center';
    context.fillText(roomData.name || `Room ${index + 1}`, 256, 70);

    const texture = new THREE.CanvasTexture(canvas);
    const labelMaterial = new THREE.SpriteMaterial({ map: texture });
    const label = new THREE.Sprite(labelMaterial);
    label.scale.set(4, 1, 1);
    label.position.set(0, height + 1, 0);
    group.add(label);

    scene.add(group);

    return {
        mesh: group,
        data: roomData,
        index: index,
        label: label
    };
}

// Update room color based on heat loss
function updateRoomHeatmap(room, heatLoss) {
    if (!room || !room.mesh) return;

    // Heat loss per m²
    const area = (room.data.width || 5) * (room.data.depth || 4);
    const heatLossPerM2 = heatLoss / area;

    // Color scale: green (low) -> yellow -> orange -> red (high)
    let color;
    if (heatLossPerM2 < 30) {
        color = new THREE.Color(0x4CAF50); // Green
    } else if (heatLossPerM2 < 60) {
        color = new THREE.Color(0xFFC107); // Yellow
    } else if (heatLossPerM2 < 100) {
        color = new THREE.Color(0xFF5722); // Orange
    } else {
        color = new THREE.Color(0xD32F2F); // Red
    }

    // Update wall materials
    room.mesh.children.forEach(child => {
        if (child.type === 'Mesh' && child.geometry.type === 'BoxGeometry') {
            child.material.color = color;
        }
    });
}

// Select room
function selectRoom(room) {
    // Deselect previous
    if (selectedRoom) {
        selectedRoom.mesh.children.forEach(child => {
            if (child.type === 'Mesh') {
                child.material.emissive = new THREE.Color(0x000000);
            }
        });
    }

    selectedRoom = room;

    // Highlight selected
    room.mesh.children.forEach(child => {
        if (child.type === 'Mesh') {
            child.material.emissive = new THREE.Color(0x333333);
        }
    });

    // Update selection panel
    updateSelectionPanel(room);

    // Update rooms list
    renderRoomsList();
}

// Update selection panel
function updateSelectionPanel(room) {
    const panel = document.getElementById('selectionPanel');

    if (!room) {
        panel.innerHTML = '<p class="placeholder">Click on a room to see properties</p>';
        return;
    }

    const data = room.data;
    const area = (data.width || 5) * (data.depth || 4);
    const volume = area * (data.height || 2.4);

    panel.innerHTML = `
        <div class="selection-property">
            <span class="label">Room Name:</span>
            <span class="value">${data.name || 'Unnamed'}</span>
        </div>
        <div class="selection-property">
            <span class="label">Type:</span>
            <span class="value">${data.room_type || 'Unknown'}</span>
        </div>
        <div class="selection-property">
            <span class="label">Dimensions:</span>
            <span class="value">${data.width || 5}m × ${data.depth || 4}m × ${data.height || 2.4}m</span>
        </div>
        <div class="selection-property">
            <span class="label">Floor Area:</span>
            <span class="value">${area.toFixed(1)} m²</span>
        </div>
        <div class="selection-property">
            <span class="label">Volume:</span>
            <span class="value">${volume.toFixed(1)} m³</span>
        </div>
        <div class="selection-property">
            <span class="label">Design Temp:</span>
            <span class="value">${data.design_temp || 'Auto'}°C</span>
        </div>
        <div class="selection-property">
            <span class="label">Walls:</span>
            <span class="value">${data.walls?.length || 0}</span>
        </div>
        <div class="selection-property">
            <span class="label">Windows:</span>
            <span class="value">${data.windows?.length || 0}</span>
        </div>
        <div class="selection-property">
            <span class="label">Floors:</span>
            <span class="value">${data.floors?.length || 0}</span>
        </div>
        <button class="btn btn-primary btn-block" onclick="editSelectedRoom()" style="margin-top: 15px;">
            Edit Room
        </button>
        <button class="btn btn-danger btn-block" onclick="deleteSelectedRoom()">
            Delete Room
        </button>
    `;
}

// Add new room
function addNewRoom() {
    const roomData = {
        name: `Room ${rooms.length + 1}`,
        room_type: 'Lounge',
        width: 5,
        depth: 4,
        height: 2.4,
        design_temp: 21,
        air_change_rate: null,
        walls: [],
        windows: [],
        floors: []
    };

    const roomObj = createRoomMesh(roomData, rooms.length);
    rooms.push(roomObj);
    projectData.rooms.push(roomData);

    renderRoomsList();
    selectRoom(roomObj);
    saveToLocalStorage();  // Auto-save

    // Open modal to edit
    openRoomModal(roomData, rooms.length - 1);
}

// Draw connection lines between adjacent rooms
function drawAdjacentRoomConnections() {
    // Remove old connection lines
    scene.children.filter(obj => obj.userData.isConnection).forEach(obj => scene.remove(obj));

    // Draw new connections
    rooms.forEach(room => {
        const roomData = room.data;
        if (!roomData.walls) return;

        roomData.walls.forEach(wall => {
            // Check if this wall connects to another room
            if (!wall.boundary || ['external', 'ground', 'unheated'].includes(wall.boundary)) {
                return;
            }

            const adjacentRoomData = projectData.rooms.find(r => r.name === wall.boundary);
            if (!adjacentRoomData) return;

            const adjacentRoom = rooms.find(r => r.data.name === wall.boundary);
            if (!adjacentRoom) return;

            // Draw a line between the two room centers
            const points = [];
            points.push(new THREE.Vector3(
                room.mesh.position.x,
                roomData.height / 2,
                room.mesh.position.z
            ));
            points.push(new THREE.Vector3(
                adjacentRoom.mesh.position.x,
                adjacentRoomData.height / 2,
                adjacentRoom.mesh.position.z
            ));

            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const material = new THREE.LineBasicMaterial({
                color: 0xffaa00,
                linewidth: 2,
                transparent: true,
                opacity: 0.6
            });
            const line = new THREE.Line(geometry, material);
            line.userData.isConnection = true;
            scene.add(line);
        });
    });
}

// Render rooms list
function renderRoomsList() {
    const list = document.getElementById('roomsList');

    if (rooms.length === 0) {
        list.innerHTML = '<p class="placeholder">No rooms yet</p>';
        return;
    }

    list.innerHTML = rooms.map((room, index) => {
        const data = room.data;
        const area = (data.width || 5) * (data.depth || 4);
        const isSelected = selectedRoom === room;

        return `
            <div class="room-item ${isSelected ? 'selected' : ''}" onclick="selectRoomByIndex(${index})">
                <div class="room-item-header">
                    <span class="room-item-name">${data.name || `Room ${index + 1}`}</span>
                </div>
                <div class="room-item-details">
                    ${data.room_type} • ${area.toFixed(1)}m² • ${data.height || 2.4}m high
                </div>
            </div>
        `;
    }).join('');
}

// Select room by index (from list)
function selectRoomByIndex(index) {
    if (rooms[index]) {
        selectRoom(rooms[index]);
    }
}

// Edit selected room
function editSelectedRoom() {
    if (selectedRoom) {
        openRoomModal(selectedRoom.data, selectedRoom.index);
    }
}

// Delete selected room
function deleteSelectedRoom() {
    if (!selectedRoom || !confirm('Delete this room?')) return;

    const index = selectedRoom.index;

    // Remove from scene
    scene.remove(selectedRoom.mesh);

    // Remove from arrays
    rooms.splice(index, 1);
    projectData.rooms.splice(index, 1);

    // Update indices
    rooms.forEach((room, i) => {
        room.index = i;
        room.mesh.userData.index = i;
    });

    selectedRoom = null;
    updateSelectionPanel(null);
    renderRoomsList();
}

// Set status message
function setStatus(message) {
    document.getElementById('status').textContent = message;
}

// Camera views
function setCameraView(view) {
    const distance = 20;

    switch(view) {
        case 'front':
            camera.position.set(0, 5, distance);
            camera.lookAt(0, 2, 0);
            break;
        case 'top':
            camera.position.set(0, distance, 0);
            camera.lookAt(0, 0, 0);
            break;
        case 'iso':
            camera.position.set(distance, distance, distance);
            camera.lookAt(0, 0, 0);
            break;
    }
    controls.update();
}

// Zoom controls
function zoomIn() {
    camera.zoom *= 1.2;
    camera.updateProjectionMatrix();
}

function zoomOut() {
    camera.zoom /= 1.2;
    camera.updateProjectionMatrix();
}

function resetCamera() {
    camera.position.set(15, 15, 15);
    camera.lookAt(0, 0, 0);
    camera.zoom = 1;
    camera.updateProjectionMatrix();
    controls.reset();
}

// Fabric element management
let currentWalls = [];
let currentWindows = [];
let currentFloors = [];

// Auto-save room data when editing
function autoSaveRoomData() {
    const modal = document.getElementById('roomModal');
    if (!modal || !modal.dataset.editIndex) return;

    const index = parseInt(modal.dataset.editIndex);
    if (index < 0 || index >= projectData.rooms.length) return;

    // Update the room data in projectData
    projectData.rooms[index].walls = currentWalls;
    projectData.rooms[index].windows = currentWindows;
    projectData.rooms[index].floors = currentFloors;

    // Save to localStorage
    saveToLocalStorage();
}

function addWall() {
    currentWalls.push({
        name: `Wall ${currentWalls.length + 1}`,
        area: 12,
        u_value: 0.3,
        temperature_factor: 1.0,
        boundary: 'external'
    });
    renderWalls();
}

function addWindow() {
    currentWindows.push({
        name: `Window ${currentWindows.length + 1}`,
        area: 4,
        u_value: 1.4,
        wall: 'front'  // front, back, left, right for visualization
    });
    renderWindows();
    autoSaveRoomData();
}

function addFloor() {
    currentFloors.push({
        name: `Floor ${currentFloors.length + 1}`,
        area: 20,
        u_value: 0.25,
        temperature_factor: 0.5
    });
    renderFloors();
}

function renderWalls() {
    const container = document.getElementById('wallsList');

    // Build room options for adjacent room selection
    const modal = document.getElementById('roomModal');
    const currentRoomIndex = parseInt(modal.dataset.editIndex);
    const roomOptions = projectData.rooms
        .map((room, idx) => idx !== currentRoomIndex ? `<option value="${room.name}">${room.name}</option>` : '')
        .join('');

    // Check if boundary is a room name (not 'external', 'ground', 'unheated')
    const isAdjacentRoom = (boundary) => {
        if (!boundary) return false;
        return !['external', 'ground', 'unheated'].includes(boundary);
    };

    container.innerHTML = currentWalls.map((wall, i) => `
        <div class="fabric-item">
            <div class="fabric-item-header">
                <span>${wall.name}</span>
                <button type="button" class="btn btn-danger btn-small" onclick="removeWall(${i})">×</button>
            </div>
            <div class="fabric-item-fields">
                <div>
                    <label>Name</label>
                    <input type="text" value="${wall.name}" onchange="currentWalls[${i}].name = this.value; autoSaveRoomData()">
                </div>
                <div>
                    <label>Area (m²)</label>
                    <input type="number" value="${wall.area}" step="0.1" onchange="currentWalls[${i}].area = parseFloat(this.value); autoSaveRoomData()">
                </div>
                <div>
                    <label>U-value (W/m²K)</label>
                    <input type="number" value="${wall.u_value}" step="0.01" onchange="currentWalls[${i}].u_value = parseFloat(this.value); autoSaveRoomData()">
                    <small>0.15-0.3 modern, 1.0 cavity, 1.5 solid stone</small>
                </div>
                <div>
                    <label>Boundary</label>
                    <select onchange="currentWalls[${i}].boundary = this.value; currentWalls[${i}].temperature_factor = 1.0; renderWalls(); autoSaveRoomData();">
                        <option value="external" ${wall.boundary === 'external' || !wall.boundary ? 'selected' : ''}>External</option>
                        <option value="ground" ${wall.boundary === 'ground' ? 'selected' : ''}>Ground</option>
                        <option value="unheated" ${wall.boundary === 'unheated' ? 'selected' : ''}>Unheated Space</option>
                        ${roomOptions ? '<option value="">-- Adjacent Rooms --</option>' : ''}
                        ${roomOptions}
                        ${isAdjacentRoom(wall.boundary) ? `<option value="${wall.boundary}" selected>${wall.boundary}</option>` : ''}
                    </select>
                    <small>${isAdjacentRoom(wall.boundary) ? 'Inter-room heat transfer' : 'Heat loss to outside'}</small>
                </div>
                ${!isAdjacentRoom(wall.boundary) && wall.boundary !== 'external' ? `
                <div>
                    <label>Temp Factor (0-1)</label>
                    <input type="number" value="${wall.temperature_factor || 1.0}" step="0.1" min="0" max="1" onchange="currentWalls[${i}].temperature_factor = parseFloat(this.value); autoSaveRoomData()">
                    <small>0.5 ground, 0.3 unheated</small>
                </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function renderWindows() {
    const container = document.getElementById('windowsList');
    container.innerHTML = currentWindows.map((window, i) => `
        <div class="fabric-item">
            <div class="fabric-item-header">
                <span>${window.name}</span>
                <button type="button" class="btn btn-danger btn-small" onclick="removeWindow(${i})">×</button>
            </div>
            <div class="fabric-item-fields">
                <div>
                    <label>Name</label>
                    <input type="text" value="${window.name}" onchange="currentWindows[${i}].name = this.value; autoSaveRoomData()">
                </div>
                <div>
                    <label>Area (m²)</label>
                    <input type="number" value="${window.area}" step="0.1" onchange="currentWindows[${i}].area = parseFloat(this.value); autoSaveRoomData()">
                </div>
                <div>
                    <label>U-value (W/m²K)</label>
                    <input type="number" value="${window.u_value}" step="0.1" onchange="currentWindows[${i}].u_value = parseFloat(this.value); autoSaveRoomData()">
                    <small>0.8-1.2 triple, 1.4 double, 4.8 single</small>
                </div>
                <div>
                    <label>Wall Position</label>
                    <select onchange="currentWindows[${i}].wall = this.value; autoSaveRoomData()">
                        <option value="front" ${!window.wall || window.wall === 'front' ? 'selected' : ''}>Front (North)</option>
                        <option value="back" ${window.wall === 'back' ? 'selected' : ''}>Back (South)</option>
                        <option value="left" ${window.wall === 'left' ? 'selected' : ''}>Left (West)</option>
                        <option value="right" ${window.wall === 'right' ? 'selected' : ''}>Right (East)</option>
                    </select>
                    <small>Which external wall</small>
                </div>
            </div>
        </div>
    `).join('');
}

function renderFloors() {
    const container = document.getElementById('floorsList');
    container.innerHTML = currentFloors.map((floor, i) => `
        <div class="fabric-item">
            <div class="fabric-item-header">
                <span>${floor.name}</span>
                <button type="button" class="btn btn-danger btn-small" onclick="removeFloor(${i})">×</button>
            </div>
            <div class="fabric-item-fields">
                <div>
                    <label>Name</label>
                    <input type="text" value="${floor.name}" onchange="currentFloors[${i}].name = this.value; autoSaveRoomData()">
                </div>
                <div>
                    <label>Area (m²)</label>
                    <input type="number" value="${floor.area}" step="0.1" onchange="currentFloors[${i}].area = parseFloat(this.value); autoSaveRoomData()">
                </div>
                <div>
                    <label>U-value (W/m²K)</label>
                    <input type="number" value="${floor.u_value}" step="0.01" onchange="currentFloors[${i}].u_value = parseFloat(this.value); autoSaveRoomData()">
                    <small>0.15-0.25 insulated, 0.7 uninsulated</small>
                </div>
                <div>
                    <label>Temp Factor (0-1)</label>
                    <input type="number" value="${floor.temperature_factor}" step="0.1" min="0" max="1" onchange="currentFloors[${i}].temperature_factor = parseFloat(this.value); autoSaveRoomData()">
                    <small>0.5 typical ground floor</small>
                </div>
            </div>
        </div>
    `).join('');
}

function removeWall(index) {
    currentWalls.splice(index, 1);
    renderWalls();
}

function removeWindow(index) {
    currentWindows.splice(index, 1);
    renderWindows();
}

function removeFloor(index) {
    currentFloors.splice(index, 1);
    renderFloors();
}

// Building Shell Functions
function openShellModal() {
    document.getElementById('shellModal').classList.add('active');
}

function closeShellModal() {
    document.getElementById('shellModal').classList.remove('active');
}

function createBuildingShell() {
    const width = parseFloat(document.getElementById('shellWidth').value);
    const depth = parseFloat(document.getElementById('shellDepth').value);
    const height = parseFloat(document.getElementById('shellHeight').value);
    const roomsX = parseInt(document.getElementById('shellRoomsX').value);
    const roomsZ = parseInt(document.getElementById('shellRoomsZ').value);

    // Clear existing rooms
    rooms.forEach(room => scene.remove(room.mesh));
    rooms = [];
    projectData.rooms = [];

    // Remove old shell if exists
    if (buildingShell) {
        scene.remove(buildingShell.mesh);
    }

    // Store shell data
    buildingShell = {
        width,
        depth,
        height,
        roomsX,
        roomsZ
    };

    // Create visual representation of shell
    const shellGroup = new THREE.Group();

    // Create wireframe outline
    const outlineGeometry = new THREE.EdgesGeometry(
        new THREE.BoxGeometry(width, height, depth)
    );
    const outlineMaterial = new THREE.LineBasicMaterial({
        color: 0x00ff00,
        linewidth: 3
    });
    const outline = new THREE.LineSegments(outlineGeometry, outlineMaterial);
    outline.position.y = height / 2;
    shellGroup.add(outline);

    // Create semi-transparent walls
    const wallMaterial = new THREE.MeshStandardMaterial({
        color: 0x4CAF50,
        transparent: true,
        opacity: 0.2,
        side: THREE.DoubleSide
    });

    // Floor outline
    const floorGeometry = new THREE.PlaneGeometry(width, depth);
    const floor = new THREE.Mesh(floorGeometry, wallMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = 0.05;
    shellGroup.add(floor);

    // Draw subdivision grid
    const gridMaterial = new THREE.LineBasicMaterial({
        color: 0xffaa00,
        linewidth: 2
    });

    // Vertical divisions (along X)
    for (let i = 1; i < roomsX; i++) {
        const x = -width / 2 + (i * width / roomsX);
        const points = [
            new THREE.Vector3(x, 0, -depth / 2),
            new THREE.Vector3(x, 0, depth / 2)
        ];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(geometry, gridMaterial);
        shellGroup.add(line);
    }

    // Horizontal divisions (along Z)
    for (let i = 1; i < roomsZ; i++) {
        const z = -depth / 2 + (i * depth / roomsZ);
        const points = [
            new THREE.Vector3(-width / 2, 0, z),
            new THREE.Vector3(width / 2, 0, z)
        ];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(geometry, gridMaterial);
        shellGroup.add(line);
    }

    buildingShell.mesh = shellGroup;
    scene.add(shellGroup);

    closeShellModal();
    setStatus(`Building shell created: ${width}m × ${depth}m, ${roomsX * roomsZ} rooms planned`);
}

function subdivideShell() {
    if (!buildingShell) {
        alert('Please create a building shell first!');
        return;
    }

    const { width, depth, height, roomsX, roomsZ } = buildingShell;
    const roomWidth = width / roomsX;
    const roomDepth = depth / roomsZ;

    // Create rooms in grid
    let roomIndex = 0;
    for (let z = 0; z < roomsZ; z++) {
        for (let x = 0; x < roomsX; x++) {
            // Calculate room position (centered at origin)
            const posX = -width / 2 + (x + 0.5) * roomWidth;
            const posZ = -depth / 2 + (z + 0.5) * roomDepth;

            // Create room data
            const roomData = {
                name: `Room ${String.fromCharCode(65 + z)}${x + 1}`, // A1, A2, B1, B2, etc.
                room_type: 'Lounge',
                width: roomWidth,
                depth: roomDepth,
                height: height,
                design_temp: 21,
                position_x: posX,
                position_z: posZ,
                air_change_rate: null,
                thermal_bridging: 15,
                walls: [],
                windows: [],
                floors: []
            };

            // Add walls based on position
            // North wall (front, -Z)
            if (z === 0) {
                roomData.walls.push({
                    name: 'North Wall',
                    area: roomWidth * height,
                    u_value: 0.3,
                    boundary: 'external',
                    temperature_factor: 1.0
                });
            } else {
                // Adjacent to room in row above
                const adjacentName = `Room ${String.fromCharCode(65 + z - 1)}${x + 1}`;
                roomData.walls.push({
                    name: 'North Wall',
                    area: roomWidth * height,
                    u_value: 0.5,
                    boundary: adjacentName,
                    temperature_factor: 1.0
                });
            }

            // South wall (back, +Z)
            if (z === roomsZ - 1) {
                roomData.walls.push({
                    name: 'South Wall',
                    area: roomWidth * height,
                    u_value: 0.3,
                    boundary: 'external',
                    temperature_factor: 1.0
                });
            } else {
                // Adjacent to room in row below
                const adjacentName = `Room ${String.fromCharCode(65 + z + 1)}${x + 1}`;
                roomData.walls.push({
                    name: 'South Wall',
                    area: roomWidth * height,
                    u_value: 0.5,
                    boundary: adjacentName,
                    temperature_factor: 1.0
                });
            }

            // West wall (left, -X)
            if (x === 0) {
                roomData.walls.push({
                    name: 'West Wall',
                    area: roomDepth * height,
                    u_value: 0.3,
                    boundary: 'external',
                    temperature_factor: 1.0
                });
            } else {
                // Adjacent to room on the left
                const adjacentName = `Room ${String.fromCharCode(65 + z)}${x}`;
                roomData.walls.push({
                    name: 'West Wall',
                    area: roomDepth * height,
                    u_value: 0.5,
                    boundary: adjacentName,
                    temperature_factor: 1.0
                });
            }

            // East wall (right, +X)
            if (x === roomsX - 1) {
                roomData.walls.push({
                    name: 'East Wall',
                    area: roomDepth * height,
                    u_value: 0.3,
                    boundary: 'external',
                    temperature_factor: 1.0
                });
            } else {
                // Adjacent to room on the right
                const adjacentName = `Room ${String.fromCharCode(65 + z)}${x + 2}`;
                roomData.walls.push({
                    name: 'East Wall',
                    area: roomDepth * height,
                    u_value: 0.5,
                    boundary: adjacentName,
                    temperature_factor: 1.0
                });
            }

            // Floor
            roomData.floors.push({
                name: 'Floor',
                area: roomWidth * roomDepth,
                u_value: 0.25,
                temperature_factor: 0.5
            });

            // Add to project
            projectData.rooms.push(roomData);
            const room = createRoomMesh(roomData, roomIndex);
            rooms.push(room);

            roomIndex++;
        }
    }

    // Remove shell visualization
    scene.remove(buildingShell.mesh);
    buildingShell = null;

    renderRoomsList();
    drawAdjacentRoomConnections();
    setStatus(`Building subdivided into ${roomsX * roomsZ} rooms with shared walls`);
}

// Auto-position next to adjacent room
function autoPositionNextToAdjacent() {
    // Find first wall with an adjacent room boundary
    const adjacentWall = currentWalls.find(wall => {
        return wall.boundary && !['external', 'ground', 'unheated'].includes(wall.boundary);
    });

    if (!adjacentWall) {
        alert('No adjacent room found in walls. Please set a wall boundary to an adjacent room first.');
        return;
    }

    const adjacentRoomName = adjacentWall.boundary;
    const adjacentRoomData = projectData.rooms.find(r => r.name === adjacentRoomName);

    if (!adjacentRoomData) {
        alert(`Adjacent room "${adjacentRoomName}" not found.`);
        return;
    }

    // Get current room dimensions
    const width = parseFloat(document.getElementById('roomWidth').value);
    const depth = parseFloat(document.getElementById('roomDepth').value);

    // Position to the right of the adjacent room (+X direction)
    const newX = (adjacentRoomData.position_x || 0) + (adjacentRoomData.width / 2) + (width / 2);
    const newZ = adjacentRoomData.position_z || 0;

    document.getElementById('positionX').value = newX;
    document.getElementById('positionZ').value = newZ;

    alert(`Positioned next to "${adjacentRoomName}"`);
}

// Modal functions
function openRoomModal(roomData, index) {
    const modal = document.getElementById('roomModal');

    // Fill form
    document.getElementById('roomName').value = roomData.name || '';
    document.getElementById('roomType').value = roomData.room_type || 'Lounge';
    document.getElementById('roomWidth').value = roomData.width || 5;
    document.getElementById('roomDepth').value = roomData.depth || 4;
    document.getElementById('roomHeight').value = roomData.height || 2.4;
    document.getElementById('designTemp').value = roomData.design_temp || '';
    document.getElementById('positionX').value = roomData.position_x || 0;
    document.getElementById('positionZ').value = roomData.position_z || 0;
    document.getElementById('airChangeRate').value = roomData.air_change_rate || '';
    document.getElementById('thermalBridging').value = roomData.thermal_bridging || 15;

    // Load fabric elements
    currentWalls = roomData.walls ? JSON.parse(JSON.stringify(roomData.walls)) : [];
    currentWindows = roomData.windows ? JSON.parse(JSON.stringify(roomData.windows)) : [];
    currentFloors = roomData.floors ? JSON.parse(JSON.stringify(roomData.floors)) : [];

    renderWalls();
    renderWindows();
    renderFloors();

    // Store index for saving
    modal.dataset.editIndex = index;

    modal.classList.add('active');
}

function closeRoomModal() {
    document.getElementById('roomModal').classList.remove('active');
}

function saveRoomProperties() {
    const modal = document.getElementById('roomModal');
    const index = parseInt(modal.dataset.editIndex);

    const roomData = {
        name: document.getElementById('roomName').value,
        room_type: document.getElementById('roomType').value,
        width: parseFloat(document.getElementById('roomWidth').value),
        depth: parseFloat(document.getElementById('roomDepth').value),
        height: parseFloat(document.getElementById('roomHeight').value),
        design_temp: document.getElementById('designTemp').value ? parseFloat(document.getElementById('designTemp').value) : null,
        position_x: parseFloat(document.getElementById('positionX').value),
        position_z: parseFloat(document.getElementById('positionZ').value),
        air_change_rate: document.getElementById('airChangeRate').value ? parseFloat(document.getElementById('airChangeRate').value) : null,
        thermal_bridging: parseFloat(document.getElementById('thermalBridging').value),
        walls: currentWalls,
        windows: currentWindows,
        floors: currentFloors
    };

    // Update data
    projectData.rooms[index] = roomData;
    rooms[index].data = roomData;

    // Rebuild mesh
    scene.remove(rooms[index].mesh);
    const newRoom = createRoomMesh(roomData, index);
    rooms[index] = newRoom;

    renderRoomsList();
    drawAdjacentRoomConnections();
    closeRoomModal();
    setStatus('Room updated');
    saveToLocalStorage();  // Auto-save
}

// Tabs
document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;

            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.querySelector(`.tab-content[data-tab="${tab}"]`).classList.add('active');
        });
    });

    // Initialize
    initThree();

    // Load saved project from localStorage
    loadFromLocalStorage();

    // Button events
    document.getElementById('createShell').addEventListener('click', openShellModal);
    document.getElementById('subdivideShell').addEventListener('click', subdivideShell);
    document.getElementById('addRoom').addEventListener('click', addNewRoom);
    document.getElementById('calculate').addEventListener('click', calculateHeatLoss);
    document.getElementById('newProject').addEventListener('click', newProject);
    document.getElementById('saveJson').addEventListener('click', saveJSON);
    document.getElementById('loadJson').addEventListener('click', () => document.getElementById('fileInput').click());
    document.getElementById('fileInput').addEventListener('change', handleFileLoad);

    // View options
    document.getElementById('showHeatmap').addEventListener('change', (e) => {
        showHeatmap = e.target.checked;
        // Re-render with/without heatmap
    });

    document.getElementById('showLabels').addEventListener('change', (e) => {
        showLabels = e.target.checked;
        rooms.forEach(room => {
            room.label.visible = showLabels;
        });
    });

    document.getElementById('showGrid').addEventListener('change', (e) => {
        gridHelper.visible = e.target.checked;
    });
});

// Calculate heat loss
async function calculateHeatLoss() {
    if (rooms.length === 0) {
        alert('Please add at least one room first');
        return;
    }

    setStatus('Calculating...');

    // Build room temperature map for inter-room heat transfer
    const roomTemps = {};
    projectData.rooms.forEach(room => {
        const defaultTemps = {
            'Lounge': 21, 'Dining': 21, 'Kitchen': 18,
            'Bedroom': 18, 'Bathroom': 22, 'Hall': 18
        };
        roomTemps[room.name] = room.design_temp || defaultTemps[room.room_type] || 21;
    });

    const results = {
        total_watts: 0,
        rooms: []
    };

    const externalTemp = parseFloat(document.getElementById('externalTemp').value);
    const buildingCategory = document.getElementById('buildingCategory').value;
    const defaultACH = { 'A': 1.5, 'B': 1.0, 'C': 0.6 }[buildingCategory] || 1.0;

    rooms.forEach(room => {
        const data = room.data;
        const volume = (data.width || 5) * (data.depth || 4) * (data.height || 2.4);
        const designTemp = roomTemps[data.name];

        // Fabric heat loss
        let fabricLoss = 0;

        // Walls
        let wallLoss = 0;
        let interRoomLoss = 0;
        if (data.walls) {
            data.walls.forEach(wall => {
                let tempDiff;
                // Check if boundary is an adjacent room name
                if (wall.boundary in roomTemps) {
                    // Inter-room heat transfer
                    const adjacentTemp = roomTemps[wall.boundary];
                    tempDiff = designTemp - adjacentTemp;
                    interRoomLoss += wall.area * wall.u_value * tempDiff;
                    return; // Don't add to wallLoss
                } else if (wall.boundary === 'ground') {
                    // Ground contact - use boundary_temp if set, otherwise temp_factor approach
                    const groundTemp = wall.boundary_temp !== undefined ? wall.boundary_temp : externalTemp;
                    tempDiff = designTemp - groundTemp;
                } else if (wall.boundary === 'unheated') {
                    // Unheated space - use boundary_temp if set, otherwise 18°C
                    const unheatedTemp = wall.boundary_temp !== undefined ? wall.boundary_temp : 18;
                    tempDiff = designTemp - unheatedTemp;
                } else {
                    // External or default
                    tempDiff = designTemp - externalTemp;
                }
                wallLoss += wall.area * wall.u_value * tempDiff * (wall.temperature_factor || 1.0);
            });
        }
        fabricLoss = wallLoss + interRoomLoss;

        // Windows
        if (data.windows) {
            data.windows.forEach(window => {
                const tempDiff = designTemp - externalTemp;
                fabricLoss += window.area * window.u_value * tempDiff;
            });
        }

        // Floors
        if (data.floors) {
            data.floors.forEach(floor => {
                const tempFactor = floor.temperature_factor || 0.5;
                const tempDiff = (designTemp - externalTemp) * tempFactor;
                fabricLoss += floor.area * floor.u_value * tempDiff;
            });
        }

        // Thermal bridging
        const bridgingFactor = (data.thermal_bridging || 15) / 100;
        const fabricWithBridging = fabricLoss * (1 + bridgingFactor);

        // Ventilation heat loss
        const ach = data.air_change_rate || defaultACH;
        const tempDiff = designTemp - externalTemp;
        const ventLoss = 0.33 * ach * volume * tempDiff;

        // Total
        const totalLoss = fabricWithBridging + ventLoss;

        results.rooms.push({
            name: data.name,
            loss: totalLoss,
            fabric: fabricWithBridging,
            ventilation: ventLoss
        });
        results.total_watts += totalLoss;

        // Update heatmap
        if (showHeatmap) {
            updateRoomHeatmap(room, totalLoss);
        }
    });

    displayResults(results);
    setStatus('Calculation complete');
}

// Display results
function displayResults(results) {
    const container = document.getElementById('results');

    const html = `
        <div class="result-box">
            <div class="label">Total Heat Loss</div>
            <div class="value">${(results.total_watts / 1000).toFixed(2)}</div>
            <div class="label">kW</div>
        </div>
        ${results.rooms.map(room => `
            <div class="room-result">
                <span class="name">${room.name}</span>
                <span class="value">${room.loss.toFixed(0)}W</span>
            </div>
        `).join('')}
    `;

    container.innerHTML = html;
}

// LocalStorage persistence
function saveToLocalStorage() {
    try {
        // Update project data from form
        projectData.building_name = document.getElementById('buildingName').value;
        projectData.postcode_area = document.getElementById('postcodeArea').value;
        projectData.building_category = document.getElementById('buildingCategory').value;
        projectData.external_temp = parseFloat(document.getElementById('externalTemp').value);

        localStorage.setItem('mcs_heat_loss_project', JSON.stringify(projectData));
    } catch (e) {
        console.error('Failed to save to localStorage:', e);
    }
}

function loadFromLocalStorage() {
    try {
        const saved = localStorage.getItem('mcs_heat_loss_project');
        if (saved) {
            projectData = JSON.parse(saved);

            // Update form fields
            document.getElementById('buildingName').value = projectData.building_name || 'My House';
            document.getElementById('postcodeArea').value = projectData.postcode_area || 'M';
            document.getElementById('buildingCategory').value = projectData.building_category || 'B';
            document.getElementById('externalTemp').value = projectData.external_temp || -3.1;

            // Rebuild rooms
            if (projectData.rooms && projectData.rooms.length > 0) {
                rooms = [];
                scene.clear();
                initLighting();
                initGrid();

                projectData.rooms.forEach(roomData => {
                    const roomMesh = createRoomMesh(roomData);
                    scene.add(roomMesh);
                    rooms.push({ data: roomData, mesh: roomMesh });
                });

                updateRoomList();
            }

            return true;
        }
    } catch (e) {
        console.error('Failed to load from localStorage:', e);
    }
    return false;
}

// JSON functions
function saveJSON() {
    projectData.building_name = document.getElementById('buildingName').value;
    projectData.postcode_area = document.getElementById('postcodeArea').value;
    projectData.building_category = document.getElementById('buildingCategory').value;
    projectData.external_temp = parseFloat(document.getElementById('externalTemp').value);

    const json = JSON.stringify(projectData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectData.building_name.replace(/\s+/g, '_')}_3d_heat_loss.json`;
    a.click();
    URL.revokeObjectURL(url);

    setStatus('Project saved');
    saveToLocalStorage();  // Also save to localStorage
}

function handleFileLoad(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            projectData = JSON.parse(e.target.result);

            // Clear existing
            rooms.forEach(room => scene.remove(room.mesh));
            rooms = [];

            // Rebuild
            projectData.rooms.forEach((roomData, i) => {
                const room = createRoomMesh(roomData, i);
                rooms.push(room);
            });

            document.getElementById('buildingName').value = projectData.building_name;
            document.getElementById('postcodeArea').value = projectData.postcode_area;
            document.getElementById('buildingCategory').value = projectData.building_category;
            document.getElementById('externalTemp').value = projectData.external_temp;

            renderRoomsList();
            drawAdjacentRoomConnections();
            setStatus('Project loaded');
        } catch (error) {
            alert('Error loading file: ' + error.message);
        }
    };
    reader.readAsText(file);
}

function newProject() {
    if (rooms.length > 0 && !confirm('Clear all rooms and start new project?')) {
        return;
    }

    rooms.forEach(room => scene.remove(room.mesh));
    rooms = [];
    projectData.rooms = [];
    selectedRoom = null;
    buildingShell = null;

    // Clear localStorage
    localStorage.removeItem('mcs_heat_loss_project');

    // Reset form to defaults
    projectData = {
        building_name: 'My House',
        postcode_area: 'M',
        building_category: 'B',
        external_temp: -3.1,
        rooms: []
    };
    document.getElementById('buildingName').value = 'My House';
    document.getElementById('postcodeArea').value = 'M';
    document.getElementById('buildingCategory').value = 'B';
    document.getElementById('externalTemp').value = -3.1;

    updateSelectionPanel(null);
    renderRoomsList();
    document.getElementById('results').innerHTML = '<p class="placeholder">Click calculate to see results</p>';

    setStatus('New project created');
}
