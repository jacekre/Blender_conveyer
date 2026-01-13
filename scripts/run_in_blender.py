"""
SIMPLIFIED SCRIPT FOR RUNNING IN BLENDER GUI
Copy this entire script into Blender's Text Editor and press Alt+P to run

This script doesn't require saving the .blend file first.
"""

import bpy
import sys
import os

# IMPORTANT: Set this to your project directory
PROJECT_DIR = r"D:\Github\Blender_conveyer"

# Add scripts directory to Python path
scripts_dir = os.path.join(PROJECT_DIR, "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

print(f"Using project directory: {PROJECT_DIR}")
print(f"Scripts directory: {scripts_dir}")

# Now import and run main
try:
    # Force reload - clear all cached modules first
    print("\nClearing cached modules...")
    modules_to_clear = ['scene_setup', 'camera_config', 'lighting_setup', 'render_manager', 'main']
    for mod_name in modules_to_clear:
        if mod_name in sys.modules:
            del sys.modules[mod_name]
            print(f"  Cleared {mod_name} from cache")

    print("Importing fresh modules...\n")
    import main

    # Run with options
    # Set render=False to only setup scene without rendering
    # Set render=True to render all frames (takes time!)
    main.main(render=False, preview=False)

    print("\n" + "="*60)
    print("Scene setup complete!")
    print("To render: change render=True in this script")
    print("To preview animation: click play button in timeline")
    print("="*60)

except Exception as e:
    print(f"\n ERROR: {e}")
    import traceback
    traceback.print_exc()
