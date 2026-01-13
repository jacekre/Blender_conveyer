"""
Asset Exporter Script
Use this script to export object configurations from your .blend file.
Run this in Blender's Scripting workspace to extract asset configurations.

Usage:
    1. Open Conveyer_v2.blend in Blender
    2. Open the Scripting workspace
    3. Open this file and run it (Alt+P)
    4. Check the System Console for the output
    5. Copy the printed configuration into assets_config.py
"""

import bpy
import json
from mathutils import Euler, Matrix


def export_object_config(obj, include_data=False):
    """
    Export a single object's configuration
    
    Args:
        obj (bpy.types.Object): The object to export
        include_data (bool): Include full mesh data (advanced)
    
    Returns:
        dict: Object configuration
    """
    config = {
        "name": obj.name,
        "type": obj.type.lower(),
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "properties": {}
    }
    
    # Extract material colors if present
    try:
        if obj.data and hasattr(obj.data, 'materials') and obj.data.materials:
            mat = obj.data.materials[0]
            if mat is not None and hasattr(mat, 'use_nodes'):
                try:
                    if mat.use_nodes:
                        bsdf = mat.node_tree.nodes.get('Principled BSDF')
                        if bsdf:
                            base_color = bsdf.inputs['Base Color'].default_value
                            config["properties"]["material_color"] = list(base_color)
                            roughness = bsdf.inputs['Roughness'].default_value
                            config["properties"]["roughness"] = roughness
                except (AttributeError, KeyError):
                    # Material structure might be different, skip material extraction
                    pass
    except (AttributeError, IndexError):
        # Object might not have data or materials, skip
        pass
    
    # Include custom properties (only serializable types)
    try:
        for key in obj.keys():
            if not key.startswith('_'):
                value = obj[key]
                # Only include properties that can be serialized (exclude bpy objects, addresses, etc.)
                if isinstance(value, (str, int, float, bool, list, dict)):
                    config["properties"][key] = value
                # Skip bpy ID properties and other non-serializable types
    except (AttributeError, TypeError):
        pass
    
    return config


def export_scene_config(exclude_cameras=True, exclude_lights=True):
    """
    Export all selected objects (or all objects) as configuration
    
    Args:
        exclude_cameras (bool): Skip camera objects
        exclude_lights (bool): Skip light objects
    
    Returns:
        dict: Complete assets configuration
    """
    
    # Get selected objects, or all objects if none selected
    objects = bpy.context.selected_objects if bpy.context.selected_objects else bpy.data.objects
    
    assets = []
    for obj in objects:
        # Skip camera and light if requested
        if exclude_cameras and obj.type == 'CAMERA':
            continue
        if exclude_lights and obj.type == 'LIGHT':
            continue
        
        asset_config = export_object_config(obj)
        assets.append(asset_config)
    
    return {
        "assets": assets
    }


def print_config_as_python():
    """
    Print configuration in Python dictionary format
    Ready to copy-paste into assets_config.py
    """
    config = export_scene_config()
    
    print("\n" + "="*80)
    print("ASSETS CONFIGURATION - Copy this into assets_config.py")
    print("="*80 + "\n")
    
    print("ASSETS_CONFIG = {")
    print('    "assets": [')
    
    for i, asset in enumerate(config["assets"]):
        print("        {")
        print(f'            "name": "{asset["name"]},')
        print(f'            "type": "{asset["type"]},')
        print(f'            "location": {asset["location"]},')
        print(f'            "rotation": {asset["rotation"]},')
        print(f'            "scale": {asset["scale"]},')
        print(f'            "properties": {asset["properties"]},')
        print('            "enabled": True')
        print("        }" + ("," if i < len(config["assets"]) - 1 else ""))
    
    print("    ]")
    print("}")
    
    print("\n" + "="*80)
    print(f"Total objects exported: {len(config['assets'])}")
    print("="*80 + "\n")


def save_config_to_json(filename="assets_export.json"):
    """
    Save configuration to a JSON file
    
    Args:
        filename (str): Output filename
    """
    config = export_scene_config()
    
    # Get the directory of the current .blend file
    blend_dir = bpy.path.abspath("//")
    filepath = f"{blend_dir}{filename}"
    
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to: {filepath}")


# Run the export
if __name__ == "__main__":
    print("\nBlender Asset Exporter")
    print("-" * 80)
    print("\nInstructions:")
    print("1. Select the objects you want to export (Shift+Click)")
    print("2. Run this script")
    print("3. Check the System Console for output")
    print("4. Copy the configuration into assets_config.py")
    print("\nAlternatively, it will export ALL objects if nothing is selected.\n")
    
    # Print Python format
    print_config_as_python()
    
    # Optional: Also save to JSON
    # save_config_to_json()
