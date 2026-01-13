# Assets Configuration Guide

## Overview

This system allows you to store Blender object configurations as Python scripts, making it easy to:
- Reproduce your scene setup
- Version control your modifications
- Automate asset creation
- Modify properties programmatically

## Workflow

### Step 1: Export Your Objects from Conveyer_v2.blend

1. **Open** `Conveyer_v2.blend` in Blender
2. **Go to** Scripting workspace (top menu)
3. **Open** `scripts/export_assets.py` in the text editor
4. **Select the objects** you want to export (Shift+Click in viewport)
   - Or leave nothing selected to export ALL objects
5. **Run the script** (Alt+P or click ▶ button)
6. **Check System Console** (Window > Toggle System Console on Windows)
7. **Copy the output** - it will show Python dictionary format

### Step 2: Add Configuration to assets_config.py

1. **Open** `scripts/assets_config.py`
2. **Paste** the exported configuration into the `ASSETS_CONFIG` dictionary
3. **Modify** properties as needed:
   ```python
   ASSETS_CONFIG = {
       "assets": [
           {
               "name": "YourAsset",
               "type": "mesh",  # or "sphere", "cylinder", "empty", etc.
               "location": (0.5, 1.2, 0.3),  # (x, y, z)
               "rotation": (0, 0, 0),  # in radians (0-2π)
               "scale": (1, 1, 1),  # (x, y, z)
               "properties": {
                   "material_color": (1.0, 0.0, 0.0, 1.0),  # RGBA
                   "roughness": 0.5,
               },
               "enabled": True  # Set to False to skip loading
           }
       ]
   }
   ```

### Step 3: Use in Your Script

Add to `main.py`:

```python
from assets_config import load_assets

# In your scene setup function:
def setup_scene(config):
    # ... other setup code ...
    
    # Load custom assets
    load_assets()
```

Or run directly in Blender:
```
blender --background --python scripts/assets_config.py
```

## Common Asset Types

| Type | Description |
|------|-------------|
| `mesh` | Cube or imported mesh |
| `sphere` | UV Sphere |
| `cylinder` | Cylinder |
| `empty` | Empty object (no geometry) |
| `light` | Light source |
| `camera` | Camera object |

## Importing from External .blend Files

If your assets are in separate .blend files:

```python
{
    "name": "BottleAsset",
    "type": "model",
    "path": "../assets/bottles.blend",  # Path relative to project
    "location": (0, 0, 0),
    "rotation": (0, 0, 0),
    "scale": (1, 1, 1),
    "properties": {},
    "enabled": True
}
```

## Advanced: Custom Properties

Store any custom data:

```python
"properties": {
    "material_color": (0.8, 0.2, 0.1, 1.0),
    "custom_id": 42,
    "description": "My custom asset"
}
```

Access in Blender:
```python
obj = bpy.data.objects["AssetName"]
custom_id = obj["custom_id"]  # Returns 42
```

## Tips & Tricks

### Rotation
- Use radians (0 to 2π, or 0° to 360°)
- Convert degrees: `import math; math.radians(45)`
- Blender uses Euler angles (XYZ order)

### Disabling Assets
```python
"enabled": False  # Object won't be loaded
```

### Organizing with Collections
```python
def load_assets_organized():
    """Load assets into organized collections"""
    for asset_config in ASSETS_CONFIG["assets"]:
        obj = create_custom_object(asset_config)
        # Add to collection based on type
        collection_name = f"{asset_config['type']}_objects"
        # ... create collection and link object ...
```

### Randomization
```python
import random

# Modify location randomly when loading
asset = ASSETS_CONFIG["assets"][0].copy()
asset["location"] = (
    random.uniform(-1, 1),
    random.uniform(-1, 1),
    asset["location"][2]
)
create_custom_object(asset)
```

## Troubleshooting

### Objects not appearing
- Check `"enabled": True` in config
- Verify coordinates aren't outside view
- Check if objects are hidden in outliner (eye icon)

### Materials not applying
- Ensure object has a mesh (not empty)
- Check Shading workspace - verify material nodes exist

### External files not importing
- Verify path is correct and relative to project
- Use forward slashes `/` in paths
- Check object name matches exactly

## Example: Complete Setup

```python
# scripts/assets_config.py

ASSETS_CONFIG = {
    "assets": [
        {
            "name": "SupportFrame",
            "type": "mesh",
            "location": (0, 0, 0.5),
            "rotation": (0, 0, 0),
            "scale": (2, 2, 0.1),
            "properties": {
                "material_color": (0.3, 0.3, 0.3, 1.0),
                "roughness": 0.6
            },
            "enabled": True
        },
        {
            "name": "Lighting_Ring",
            "type": "sphere",
            "location": (0, 0, 2.0),
            "rotation": (0, 0, 0),
            "scale": (1.5, 1.5, 1.5),
            "properties": {
                "emissive": True
            },
            "enabled": True
        }
    ]
}
```

Then in `main.py`:
```python
from assets_config import load_assets

# After basic scene setup
load_assets()
```

Done! Your assets are now version-controlled and reproducible.
