# MCS Heat Loss Calculator - 3D Web Application

An interactive 3D heat loss calculator for building heat pump system design. Build your house in 3D, visualize heat loss, and export to JSON.

## 🚀 Features

### 3D Visualization
- **Interactive 3D modeling** - Build rooms in 3D space with Three.js
- **Heat loss heatmap** - Color-coded visualization (green=low, yellow=medium, red=high heat loss)
- **Real-time labels** - Room names displayed in 3D
- **Multiple camera views** - Front, Top, Isometric
- **Orbit controls** - Rotate, zoom, pan with mouse

### Room Building
- **Drag-and-drop interface** - Easy room creation
- **Customizable dimensions** - Width, depth, height
- **Fabric elements** - Add walls, windows, floors
- **U-value configuration** - Set thermal properties
- **Room types** - Lounge, Kitchen, Bedroom, Bathroom, etc.

### Heat Loss Calculation
- **BS EN 12831 methodology** - Industry-standard formulas
- **Room-by-room breakdown** - See heat loss for each space
- **Building categories** - A (leaky), B (standard), C (tight)
- **Custom ACH values** - Override with blower door test results
- **Temperature factors** - Ground contact, unheated spaces

### Data Management
- **JSON export/import** - Save and load projects
- **GitHub Pages ready** - Static hosting, no server needed
- **Offline capable** - Works after first load
- **No data tracking** - Everything stays in your browser

## 📖 How to Use

### 1. Getting Started

**Option A: GitHub Pages (Recommended)**
- Visit: `https://yourusername.github.io/python_mcs_heatloss/web/`
- No installation needed!

**Option B: Local**
```bash
cd python_mcs_heatloss/web
# Open index.html in your browser
# Or use a local server:
python -m http.server 8000
# Then visit http://localhost:8000
```

### 2. Building Your House

#### Add Rooms
1. Click **"🏗️ New Room"** button
2. Set room name (e.g., "Lounge")
3. Choose room type
4. Set dimensions:
   - Width: 5m
   - Depth: 4m
   - Height: 2.4m
5. Click **"Save Room"**

The room appears in the 3D view!

#### Edit Rooms
1. **Click on a room** in the 3D view
2. Properties appear in right sidebar
3. Click **"Edit Room"** button
4. Modify in modal dialog:
   - **Basic Tab**: Dimensions, name, type
   - **Fabric Tab**: Add walls, windows, floors
   - **Thermal Tab**: ACH, thermal bridging

#### Navigate 3D View
- **Rotate**: Left-click and drag
- **Pan**: Right-click and drag
- **Zoom**: Scroll wheel
- **Quick Views**: Use Front/Top/3D buttons

### 3. Configure Building

**Left Sidebar → Building Config:**

- **Building Name**: Your project name
- **Postcode Area**: UK area code (M, SW, EH, etc.)
  - Auto-fills degree days and design temperature
- **Category**:
  - **A - Leaky**: Older buildings (high ACH)
  - **B - Standard**: Typical buildings
  - **C - Tight**: Modern tight buildings (low ACH)
- **External Temp**: Design external temperature (°C)

### 4. Calculate Heat Loss

1. Add all rooms
2. Configure fabric elements (walls, windows, floors)
3. Click **"Calculate Heat Loss"** button
4. View results:
   - **Total kW** - Overall heat loss
   - **Room breakdown** - Heat loss per room
   - **Heat map** - Rooms colored by heat loss intensity

### 5. Visualize Heat Loss

**Heat Map Colors:**
- 🟢 **Green**: Low heat loss (<30 W/m²) - Well insulated
- 🟡 **Yellow**: Medium heat loss (30-60 W/m²) - Standard
- 🟠 **Orange**: High heat loss (60-100 W/m²) - Poor insulation
- 🔴 **Red**: Very high heat loss (>100 W/m²) - Needs improvement

**View Options:**
- ☑️ **Show Heat Loss Colors** - Toggle heatmap
- ☑️ **Show Measurements** - Toggle room labels
- ☑️ **Show Grid** - Toggle ground grid

### 6. Save & Load Projects

**Save:**
1. Click **"💾 Save"** button
2. Downloads JSON file
3. Store for later or share

**Load:**
1. Click **"📂 Load"** button
2. Select JSON file
3. Project rebuilds in 3D

## 🎨 UI Overview

### Layout

```
┌─────────────────────────────────────────────────┐
│ 🏠 MCS Heat Loss Calculator       📄 📂 💾     │ Header
├──────────┬─────────────────────┬────────────────┤
│          │                     │                │
│ Building │                     │   Selection    │
│ Tools    │                     │   Properties   │
│          │      3D View        │                │
│ Modes    │                     ├────────────────┤
│          │   [Rotate/Zoom]     │    Results     │
│ View     │                     │                │
│ Options  │                     ├────────────────┤
│          │                     │   Rooms List   │
│ Config   │                     │                │
│          │                     │                │
└──────────┴─────────────────────┴────────────────┘
 Left Sidebar   Viewport         Right Sidebar
```

### Controls

**Toolbar (Top):**
- 📄 New - Start fresh project
- 📂 Load - Import JSON
- 💾 Save - Export JSON

**Left Sidebar:**
- 🏗️ New Room - Add room
- 👆 Select - Selection mode
- 🧱 Wall - Wall editing mode
- 🪟 Window - Window editing mode
- 🔍+/- Zoom controls
- 🔄 Reset camera

**Right Sidebar:**
- 🎯 Selection - Current room properties
- 📊 Results - Heat loss calculations
- 📋 Rooms List - All rooms

## 📐 Room Configuration

### Basic Properties

| Property | Description | Example |
|----------|-------------|---------|
| Name | Room identifier | "Living Room" |
| Type | Room category | Lounge, Kitchen, Bedroom |
| Width | Room width (m) | 5.0 |
| Depth | Room depth (m) | 4.0 |
| Height | Room height (m) | 2.4 |
| Design Temp | Target temperature (°C) | 21 (or Auto) |

### Fabric Elements

**Walls:**
- Name: e.g., "External Wall North"
- Area: m²
- U-value: W/m²K (0.15-2.0 typical)
- Temp Factor: 0-1 (1.0 = external, 0.5 = ground)

**Windows:**
- Name: e.g., "Front Window"
- Area: m²
- U-value: W/m²K (0.8-4.8 typical)

**Floors:**
- Name: e.g., "Ground Floor"
- Area: m²
- U-value: W/m²K (0.15-0.7 typical)
- Temp Factor: 0-1 (0.5 = ground typical)

### Thermal Properties

**Air Change Rate (ACH):**
- Manual: From blower door test
- Auto: Based on building category + room type

Category A (Leaky):
- Lounge: 1.5 ACH
- Kitchen: 2.0 ACH
- Bedroom: 1.0 ACH

Category B (Standard):
- Lounge: 1.0 ACH
- Kitchen: 1.5 ACH
- Bedroom: 1.0 ACH

Category C (Tight):
- Lounge: 0.5 ACH
- Kitchen: 1.5 ACH
- Bedroom: 0.5 ACH

**Thermal Bridging:**
- 0.05: Modern well-detailed
- 0.10: Good detailing
- 0.15: Standard (default)
- 0.20+: Poor detailing

## 🔧 Technical Details

### Technology Stack
- **Three.js** - 3D graphics engine
- **OrbitControls** - Camera controls
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with gradients
- **HTML5** - Semantic markup

### Calculations

**Fabric Heat Loss:**
```
Q = Σ(A × U × ΔT × f)
```
- A = area (m²)
- U = U-value (W/m²K)
- ΔT = temperature difference (K)
- f = temperature factor

**Ventilation Heat Loss:**
```
Q = 0.33 × n × V × ΔT
```
- 0.33 = specific heat of air (Wh/m³K)
- n = air change rate (ACH)
- V = volume (m³)
- ΔT = temperature difference (K)

**Total:**
```
Q_total = Q_fabric + Q_ventilation + Q_thermal_bridging
```

### Browser Support
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Requirements:**
- WebGL support
- JavaScript enabled
- Modern browser (ES6+)

## 📋 JSON Format

```json
{
  "building_name": "My House",
  "postcode_area": "M",
  "building_category": "B",
  "external_temp": -3.1,
  "rooms": [
    {
      "name": "Lounge",
      "room_type": "Lounge",
      "width": 5.0,
      "depth": 4.0,
      "height": 2.4,
      "design_temp": 21,
      "air_change_rate": 0.6,
      "thermal_bridging": 0.15,
      "walls": [
        {
          "name": "External Wall",
          "area": 12,
          "u_value": 0.3,
          "temperature_factor": 1.0
        }
      ],
      "windows": [
        {
          "name": "Front Window",
          "area": 4,
          "u_value": 1.4
        }
      ],
      "floors": [
        {
          "name": "Ground Floor",
          "area": 20,
          "u_value": 0.25,
          "temperature_factor": 0.5
        }
      ]
    }
  ]
}
```

## 🎯 Tips for Accurate Results

### 1. Use Measured ACH
❌ Don't rely on category defaults
✅ Conduct blower door test
- Modern tight: 0.4-0.8 ACH
- Standard: 0.8-1.5 ACH
- Old leaky: 1.5-3.0 ACH

### 2. Survey U-Values
❌ Don't assume
✅ Measure actual construction
- Solid walls: 1.5 W/m²K
- Cavity uninsulated: 1.0 W/m²K
- Cavity insulated: 0.3 W/m²K
- Modern: 0.15-0.25 W/m²K

### 3. Check Design Temperature
❌ Don't blindly use MCS standards
✅ Use local weather data
- Check actual winter minimums
- Consider climate change
- Compare with neighbors

### 4. Model All Elements
✅ Include:
- All external walls
- All windows and doors
- All floors (ground contact)
- Thermal bridging allowance

## 🚀 Deployment (GitHub Pages)

### Setup

1. **Push to GitHub:**
```bash
git add web/
git commit -m "Add 3D heat loss calculator"
git push origin main
```

2. **Enable GitHub Pages:**
- Go to repository Settings
- Pages section
- Source: main branch
- Folder: / (root)
- Save

3. **Access:**
- URL: `https://username.github.io/python_mcs_heatloss/web/`

### Custom Domain (Optional)
1. Add CNAME file to web directory
2. Configure DNS settings
3. Enable HTTPS in GitHub Pages settings

## 🐛 Troubleshooting

**3D view not loading:**
- Check browser console for errors
- Ensure WebGL is enabled
- Try different browser

**Slow performance:**
- Reduce number of rooms
- Disable heatmap visualization
- Close other browser tabs

**Can't see rooms:**
- Use camera view buttons
- Click "Reset Camera"
- Check room dimensions > 0

**Calculations seem wrong:**
- Verify U-values are reasonable
- Check temperature difference
- Ensure ACH is set correctly

## 📝 License

Same as parent project (MCS Heat Loss Calculator)

## 🔗 Links

- [GitHub Repository](https://github.com/yourusername/python_mcs_heatloss)
- [Python Calculator](../README.md)
- [Validation Report](../VALIDATION_REPORT.md)
- [Three.js Documentation](https://threejs.org/docs/)

## 📧 Support

For issues or questions:
- Open GitHub issue
- Check documentation
- Review example JSON files

---

**Version 1.0.0** - 3D Interactive Heat Loss Calculator
Built with Three.js for GitHub Pages
