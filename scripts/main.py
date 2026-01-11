"""
Blender Conveyor Belt Simulation
Main script to setup and render conveyor belt with boxes

Usage:
    blender --background --python scripts/main.py
    or
    Run from Blender's Text Editor (Scripting workspace)
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


def load_config(config_path=None):
    """Load configuration from JSON file"""
    if config_path is None:
        # Default config path relative to script directory
        config_path = script_dir.parent / "config" / "conveyor_config.json"

    print(f"Loading configuration from: {config_path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def setup_scene(config):
    """Complete scene setup"""
    print("=" * 60)
    print("BLENDER CONVEYOR BELT SIMULATION")
    print("=" * 60)

    # Clear existing scene
    print("\n1. Clearing scene...")
    scene_setup.clear_scene()

    # Setup world
    scene_setup.setup_world_background()

    # Create conveyor belt
    print("\n2. Creating conveyor belt...")
    conveyor = scene_setup.create_conveyor_belt(config)

    # Create boxes on conveyor
    print("\n3. Creating boxes...")
    boxes = scene_setup.create_boxes_on_conveyor(config, conveyor)

    # Setup camera
    print("\n4. Setting up camera...")
    camera, camera_target, view_height = camera_config.setup_camera(config)

    # Setup render settings
    print("\n5. Configuring render settings...")
    camera_config.setup_render_settings(config)

    # Setup lighting
    print("\n6. Setting up lighting...")
    main_light = lighting_setup.setup_lighting(config)
    fill_light = lighting_setup.add_fill_lights(config)

    # Setup animation
    print("\n7. Setting up conveyor animation...")
    num_steps = render_manager.setup_animation(config, conveyor)

    print("\n" + "=" * 60)
    print("SCENE SETUP COMPLETE")
    print("=" * 60)

    return {
        'conveyor': conveyor,
        'boxes': boxes,
        'camera': camera,
        'lights': [main_light, fill_light],
        'num_steps': num_steps
    }


def main(render=True, preview=False):
    """Main execution function"""
    # Load configuration
    config = load_config()

    # Setup scene
    scene_objects = setup_scene(config)

    # Render sequence
    if render:
        print("\n8. Starting render sequence...")
        output_folder = config['render']['output_folder']
        output_path = render_manager.render_sequence(config, output_folder)

        print("\n" + "=" * 60)
        print(f"ALL DONE! Check your renders in: {output_path}")
        print("=" * 60)

    # Preview animation
    if preview:
        render_manager.preview_animation()


if __name__ == "__main__":
    # Parse command line arguments
    render = True
    preview = False

    # Check for --no-render flag
    if "--no-render" in sys.argv:
        render = False

    # Check for --preview flag
    if "--preview" in sys.argv:
        preview = True

    # Run main function
    main(render=render, preview=preview)
