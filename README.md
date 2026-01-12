# Blender Conveyor Belt Simulation

Production conveyor belt simulation in Blender 5.0 with automatic image rendering at each belt movement position.

## Specification

- **Conveyor Belt**: 2m x 0.6m x 0.02m
- **Spheres**: Diameter 0.1m, translucent, randomly placed, different colors
- **Camera**: Height 1.5m, 640x480px, covers full belt width
- **Lighting**: Strip light at 45° angle above belt
- **Movement**: Steps of 0.02m (100 positions across full length)
- **Rendering**: One image per belt position

## Project Structure

```
Blender_conveyer/
├── scripts/
│   ├── main.py              # Main script launching simulation
│   ├── scene_setup.py       # Conveyor belt and sphere creation
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

### Spheres
```json
"boxes": {
  "size": 0.1,              // Sphere diameter (m) - translucent glass-like material
  "min_count": 5,           // Minimum number of spheres
  "max_count": 15,          // Maximum number of spheres
  "z_layer_offset": 0.0001, // Height offset between spheres (m) - prevents artifacts
  "random_seed": null,      // Randomness seed (null = random)
  "random_colors": true,    // Use different colors
  "density_min": 0.3,       // Minimum material density (0.0-1.0)
  "density_max": 0.9        // Maximum material density (0.0-1.0)
}
```

**Note about sphere density:** Each sphere gets a random density between `density_min` and `density_max`:
- **Lower density (0.0-0.4)**: More transparent, water-like (high transmission, lower IOR ~1.33)
- **Medium density (0.4-0.7)**: Semi-transparent, glass-like (medium transmission, IOR ~1.45)
- **Higher density (0.7-1.0)**: Less transparent, dense glass (low transmission, higher IOR ~1.58)

The density affects:
- **Transmission**: Lower density = more light passes through (more transparent)
- **IOR (Index of Refraction)**: Higher density = stronger light bending
- **Alpha**: Higher density = more opaque appearance

**Note about sphere overlap:** Spheres can overlap randomly. Each subsequent sphere is placed
minimally higher (by `z_layer_offset`), so at intersection points newer spheres cover
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

Each image is a camera view of the current belt section with translucent spheres.

## How Sphere Overlap Works

The system allows random sphere overlap, which is more realistic for production
conveyor simulation. To prevent rendering artifacts (Z-fighting, "black holes"),
each subsequent sphere is placed minimally higher:

- Sphere #0: height = base_z
- Sphere #1: height = base_z + 0.0001m
- Sphere #2: height = base_z + 0.0002m
- etc.

The difference is microscopic (0.1mm), so visually all spheres appear at the same
level, but the rendering engine knows which is "on top" at intersection points.
The translucent material (95% transmission) allows seeing through overlapping spheres.

**Advantages of this approach:**
- ✅ No "black holes" when overlapping
- ✅ More realistic simulation (real objects can overlap too)
- ✅ All spheres can always be placed (no space constraints)
- ✅ Simpler implementation and faster execution
- ✅ Translucent material allows visibility through overlaps

## Customization

### Change number of spheres
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
**Note:** Translucent materials require more samples for good quality. Recommended minimum: 64 samples.

### Change rendering engine
```json
"engine": "EEVEE"         // Faster but less photorealistic
```
**Note:** For best translucency effects, use CYCLES engine.

### Repeatable sphere placement
```json
"random_seed": 42         // Same number = same sphere positions and densities
```

### Change sphere density range
```json
"density_min": 0.1,       // Very transparent spheres
"density_max": 0.5        // Semi-transparent spheres
```
**Examples:**
- `0.1 to 0.3`: Very transparent, water-like bubbles
- `0.3 to 0.6`: Semi-transparent, light glass (default-like)
- `0.5 to 0.9`: Dense, less transparent glass (default)
- `0.8 to 1.0`: Nearly opaque, very dense materials

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
- Decrease `samples` in config (e.g. to 32, but translucency needs more samples)
- Use `EEVEE` engine instead of `CYCLES` (but translucency won't look as good)
- Decrease camera resolution
**Note:** Translucent materials are computationally expensive - expect longer render times.

### Spheres overlap and cause artifacts ("black hole")
**Problem fixed!** The system uses Z-layering - each subsequent sphere is placed
minimally higher, so at overlap points the newer sphere is visible on top.
Translucent material allows seeing through overlaps.

If you still see artifacts, increase height offset in `config/conveyor_config.json`:
```json
"z_layer_offset": 0.0002  // Increase if problems persist (default 0.0001m)
```

### Too many/too few spheres on belt
Adjust in configuration:
```json
"min_count": 10,  // Minimum
"max_count": 20   // Maximum
```

### Spheres fall off the belt
System automatically calculates safe boundaries based on sphere diameter. If problem occurs, check sizes in configuration.

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
