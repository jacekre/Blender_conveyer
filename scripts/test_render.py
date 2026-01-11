"""
Quick test script - renders only a few frames for testing

Usage:
    blender --background --python scripts/test_render.py
"""

import bpy
import sys
import json
import os
from pathlib import Path

# Detect script directory - works both in GUI and headless mode
def get_script_dir():
    """Get the directory containing this script"""
    # Try to get from __file__ (works in headless mode)
    try:
        return Path(__file__).parent.resolve()
    except NameError:
        pass

    # Try to get from .blend file location (works in GUI)
    blend_path = bpy.data.filepath
    if blend_path:
        # Assume scripts are in a 'scripts' folder relative to .blend file
        blend_dir = Path(blend_path).parent
        scripts_dir = blend_dir / "scripts"
        if scripts_dir.exists():
            return scripts_dir

    # Last resort: use current working directory + scripts
    cwd = Path(os.getcwd())
    scripts_dir = cwd / "scripts"
    if scripts_dir.exists():
        return scripts_dir

    # If nothing works, assume we're already in scripts directory
    return cwd

# Add scripts directory to path
script_dir = get_script_dir()
print(f"Script directory: {script_dir}")

if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Import project modules
import scene_setup
import camera_config
import lighting_setup
import render_manager


def load_config():
    """Load configuration from JSON file"""
    config_path = script_dir.parent / "config" / "conveyor_config.json"

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def main():
    """Run quick test with only 3 frames"""
    print("=" * 60)
    print("QUICK TEST RENDER - 3 FRAMES ONLY")
    print("=" * 60)

    # Load configuration
    config = load_config()

    # Clear and setup scene
    print("\n1. Setting up scene...")
    scene_setup.clear_scene()
    scene_setup.setup_world_background()

    conveyor = scene_setup.create_conveyor_belt(config)
    boxes = scene_setup.create_boxes_on_conveyor(config, conveyor)

    print("\n2. Setting up camera and lighting...")
    camera, camera_target, view_height = camera_config.setup_camera(config)
    camera_config.setup_render_settings(config)

    main_light = lighting_setup.setup_lighting(config)
    fill_light = lighting_setup.add_fill_lights(config)

    print("\n3. Setting up animation...")
    num_steps = render_manager.setup_animation(config, conveyor)

    # Render only first 3 frames for testing
    print("\n4. Rendering test frames (0, 50, 99)...")
    test_frames = [0, 50, 99]  # Beginning, middle, end

    for idx in test_frames:
        render_manager.render_single_position(config, idx, "renders/test")

    print("\n" + "=" * 60)
    print("TEST COMPLETE! Check renders/test/ folder")
    print("If satisfied, run main.py for full sequence")
    print("=" * 60)


if __name__ == "__main__":
    main()
