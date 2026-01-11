# Blender Conveyor Belt Simulation

Production conveyor belt simulation in Blender 5.0 with automatic image rendering at each belt movement position.

## Specification

- **Conveyor Belt**: 2m x 0.6m x 0.02m
- **Boxes**: 0.1m x 0.1m x 0.1m, randomly placed, different colors
- **Camera**: Height 1.5m, 640x480px, covers full belt width
- **Lighting**: Strip light at 45° angle above belt
- **Movement**: Steps of 0.02m (100 positions across full length)
- **Rendering**: One image per belt position

## Project Structure

```
Blender_conveyer/
├── scripts/
│   ├── main.py              # Main script launching simulation
│   ├── scene_setup.py       # Conveyor belt and box creation
│   ├── camera_config.py     # Camera and rendering configuration
│   ├── lighting_setup.py    # Scene lighting
│   └── render_manager.py    # Sequence rendering system
├── config/
│   └── conveyor_config.json # Parameter configuration
├── renders/                 # Generated images (created automatically)
└── README.md
```

## Installation and Usage

### Requirements
- Blender 5.0 or newer
- Python 3.11+ (built into Blender)

### Method 1: Headless Mode

Background rendering without GUI:

```bash
blender --background --python scripts/main.py
```

### Method 2: In Blender GUI - EASIEST

**Method A: Using helper script (recommended)**

1. Open Blender 5.0
2. Go to **Scripting** tab
3. Open file `scripts/run_in_blender.py` (Text → Open)
4. **IMPORTANT**: Make sure the `PROJECT_DIR` path on line 12 is correct
5. Click **Run Script** (▶) or press `Alt+P`

**Method B: Direct main.py execution**

1. First save an empty .blend file in the main project folder: `File → Save As → Conveyer_v1.blend`
2. Go to **Scripting** tab
3. Open file `scripts/main.py` (Text → Open)
4. Click **Run Script** or press `Alt+P`

### Method 3: Import and run in Python console

In Blender console (Scripting → Python Console):

```python
import sys
sys.path.insert(0, r"D:\Github\Blender_conveyer\scripts")

import main
main.main(render=False)  # render=False = setup only without rendering
```

## Configuration

Edit `config/conveyor_config.json` file to adjust parameters:

### Conveyor Belt
```json
"conveyor": {
  "length": 2.0,        // Belt length (m)
  "width": 0.6,         // Belt width (m)
  "thickness": 0.02,    // Belt thickness (m)
  "step_size": 0.02     // Movement step size (m)
}
```

### Boxes
```json
"boxes": {
  "size": 0.1,              // Cube size (m)
  "min_count": 5,           // Minimum number of boxes
  "max_count": 15,          // Maximum number of boxes
  "z_layer_offset": 0.0001, // Height offset between boxes (m) - prevents artifacts
  "random_seed": null,      // Randomness seed (null = random)
  "random_colors": true     // Use different colors
}
```

**Note about box overlap:** Boxes can overlap randomly. Each subsequent box is placed
minimally higher (by `z_layer_offset`), so at intersection points newer boxes cover
older ones. This prevents rendering artifacts ("black holes") when objects overlap.

### Camera
```json
"camera": {
  "height": 1.5,        // Camera height above belt (m)
  "resolution_x": 640,  // Image width (px)
  "resolution_y": 480   // Image height (px)
}
```

### Lighting
```json
"lighting": {
  "type": "area",                // Light type
  "angle_degrees": 45,           // Tilt angle (degrees)
  "distance_from_conveyor": 1.0, // Distance from belt (m)
  "strength": 100,               // Light power (W)
  "size": 2.0,                   // Strip size (m)
  "use_fill_light": false        // Additional fill light
}
```

**Note about `use_fill_light`:**
- `false` (default) - **Recommended for industrial simulation**
  - Only one main light at 45° angle
  - Realistic shadows and contrast
  - Simulates real machine vision conditions
- `true` - Adds weaker light from opposite side
  - Softer shadows
  - Better for visualization/presentation
  - **NOT recommended for testing vision algorithms**

### Rendering
```json
"render": {
  "output_folder": "renders",  // Output folder
  "file_format": "PNG",        // Format (PNG, JPEG, etc.)
  "engine": "CYCLES",          // Engine (CYCLES or EEVEE)
  "samples": 64,               // Number of samples (quality)
  "use_denoising": true        // Use denoising
}
```

## Usage Options

### Setup only without rendering
```bash
blender --background --python scripts/main.py -- --no-render
```

### With animation preview (requires GUI)
```python
import main
main.main(render=False, preview=True)
```

## Output

Rendered images are saved in `renders/` folder as:
- `frame_0001.png` - first belt position
- `frame_0002.png` - second position
- ...
- `frame_0100.png` - last position

Each image is a camera view of the current belt section with boxes.

## How Box Overlap Works

The system allows random box overlap, which is more realistic for production
conveyor simulation. To prevent rendering artifacts (Z-fighting, "black holes"),
each subsequent box is placed minimally higher:

- Box #0: height = base_z
- Box #1: height = base_z + 0.0001m
- Box #2: height = base_z + 0.0002m
- etc.

The difference is microscopic (0.1mm), so visually all boxes appear at the same
level, but the rendering engine knows which is "on top" at intersection points.

**Advantages of this approach:**
- ✅ No "black holes" when overlapping
- ✅ More realistic simulation (real objects can overlap too)
- ✅ All boxes can always be placed (no space constraints)
- ✅ Simpler implementation and faster execution

## Customization

### Change number of boxes
In `config/conveyor_config.json` set:
```json
"min_count": 10,
"max_count": 20
```

### Change rendering quality
```json
"samples": 128,           // More samples = better quality, longer time
"use_denoising": true
```

### Change rendering engine
```json
"engine": "EEVEE"         // Faster but less photorealistic
```

### Repeatable box placement
```json
"random_seed": 42         // Same number = same box positions
```

### Enable fill light (NOT for industrial simulation!)
```json
"use_fill_light": true    // Adds additional light (visualization only)
```
**Warning:** Keep `false` if testing vision algorithms - you want realistic conditions!

## Animation Structure

- **Frame 1**: Belt at position 0m (start)
- **Frame 2**: Belt moved by 0.02m
- **Frame 3**: Belt moved by 0.04m
- ...
- **Frame 100**: Belt moved by 1.98m (end)

Each frame = one rendering position.

## Troubleshooting

### Error "No module named 'scene_setup'" or similar
This error occurs when Blender cannot find project modules. Solutions:

**Solution 1 (best):** Use the `run_in_blender.py` script:
- Open file `scripts/run_in_blender.py` in Blender's Text Editor
- Make sure the `PROJECT_DIR` path on line 12 points to your project directory
- Run the script (Alt+P)

**Solution 2:** Save .blend file in main project folder:
- File → Save As → `Conveyer_v1.blend` (in folder `D:\Github\Blender_conveyer\`)
- Then run `main.py` from Text Editor

**Solution 3:** Manual path setting in console:
```python
import sys
sys.path.insert(0, r"D:\Github\Blender_conveyer\scripts")  # Change to your path!
```
Then run the script.

### GPU not being used
In `camera_config.py:66-68` change `CUDA` to `OPENCL` or `METAL` depending on your graphics card.

### Rendering takes too long
- Decrease `samples` in config (e.g. to 32)
- Use `EEVEE` engine instead of `CYCLES`
- Decrease camera resolution

### Boxes overlap and cause artifacts ("black hole")
**Problem fixed!** The system uses Z-layering - each subsequent box is placed
minimally higher, so at overlap points the newer box is visible on top.

If you still see artifacts, increase height offset in `config/conveyor_config.json`:
```json
"z_layer_offset": 0.0002  // Increase if problems persist (default 0.0001m)
```

### Too many/too few boxes on belt
Adjust in configuration:
```json
"min_count": 10,  // Minimum
"max_count": 20   // Maximum
```

### Boxes fall off the belt
System automatically calculates safe boundaries. If problem occurs, check sizes in configuration.

## Useful Commands

### Check Blender version
```bash
blender --version
```

### Render only one frame (test)
In Blender console:
```python
import render_manager
render_manager.render_single_position(config, position_index=0)
```

### Export scene to .blend
After running the script:
```python
import bpy
bpy.ops.wm.save_as_mainfile(filepath="D:/Github/Blender_conveyer/conveyor_scene.blend")
```

## License

Open-source project for educational and commercial use.
