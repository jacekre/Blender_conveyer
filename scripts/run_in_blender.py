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
    # Import fresh (reload if already imported)
    if 'main' in sys.modules:
        import importlib
        importlib.reload(sys.modules['scene_setup'])
        importlib.reload(sys.modules['camera_config'])
        importlib.reload(sys.modules['lighting_setup'])
        importlib.reload(sys.modules['render_manager'])
        importlib.reload(sys.modules['main'])

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
