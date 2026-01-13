"""
Assets Configuration Script
Define all custom objects, models, and assets added to the scene.
This script stores the configuration of manually-added objects for reproducibility.

Usage:
    Import in main.py or run independently:
    from assets_config import ASSETS_CONFIG, load_assets
"""

# Asset configurations - Define each asset's properties
ASSETS_CONFIG = {
    "assets": [
        {
            "name": "Asset_001",
            "type": "model",  # "model", "mesh", "empty", "light", etc.
            "path": "path/to/asset.blend",  # If importing from external file
            "location": (0, 0, 0),  # (x, y, z) position
            "rotation": (0, 0, 0),  # (x, y, z) rotation in radians
            "scale": (1, 1, 1),  # (x, y, z) scale
            "properties": {
                # Add custom properties specific to this asset
                # "material_color": (1.0, 0.0, 0.0, 1.0),
                # "roughness": 0.5,
            },
            "enabled": True
        },
        # Add more assets here...
    ]
}


def import_asset_from_blend(asset_path, asset_name, collection=None):
    """
    Import an asset from an external .blend file
    
    Args:
        asset_path (str): Path to the .blend file containing the asset
        asset_name (str): Name of the object to import from the .blend file
        collection (str): Optional collection name to organize imports
    
    Returns:
        bpy.types.Object: The imported object
    """
    import bpy
    import os
    
    if not os.path.exists(asset_path):
        print(f"Warning: Asset file not found: {asset_path}")
        return None
    
    # Import from blend file
    with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
        if asset_name in data_from.objects:
            data_to.objects = [asset_name]
        else:
            print(f"Warning: Object '{asset_name}' not found in {asset_path}")
            return None
    
    # Get the imported object
    imported_obj = bpy.context.scene.objects.get(asset_name)
    
    # Organize into collection if specified
    if collection and imported_obj:
        if collection not in bpy.data.collections:
            col = bpy.data.collections.new(collection)
            bpy.context.scene.collection.children.link(col)
        col = bpy.data.collections[collection]
        col.objects.link(imported_obj)
        # Remove from default collection if it exists
        for coll in imported_obj.users_collection:
            if coll.name != collection:
                coll.objects.unlink(imported_obj)
    
    return imported_obj


def create_custom_object(asset_config):
    """
    Create or import a custom object based on configuration
    
    Args:
        asset_config (dict): Configuration dictionary for the asset
    
    Returns:
        bpy.types.Object: The created/imported object
    """
    import bpy
    
    name = asset_config.get("name", "Asset")
    asset_type = asset_config.get("type", "mesh")
    location = asset_config.get("location", (0, 0, 0))
    rotation = asset_config.get("rotation", (0, 0, 0))
    scale = asset_config.get("scale", (1, 1, 1))
    properties = asset_config.get("properties", {})
    
    obj = None
    
    # Import from external file if path provided
    if "path" in asset_config and asset_config["path"]:
        obj = import_asset_from_blend(asset_config["path"], name)
    else:
        # Create primitive based on type
        if asset_type == "mesh":
            bpy.ops.mesh.primitive_cube_add(location=location)
            obj = bpy.context.active_object
        elif asset_type == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(location=location)
            obj = bpy.context.active_object
        elif asset_type == "cylinder":
            bpy.ops.mesh.primitive_cylinder_add(location=location)
            obj = bpy.context.active_object
        elif asset_type == "empty":
            obj = bpy.data.objects.new(name, None)
            bpy.context.scene.collection.objects.link(obj)
        else:
            print(f"Warning: Unknown asset type '{asset_type}'")
            return None
    
    if obj:
        obj.name = name
        
        # Apply transforms
        obj.location = location
        obj.rotation_euler = rotation
        obj.scale = scale
        bpy.context.view_layer.update()
        
        # Apply custom properties
        for prop_name, prop_value in properties.items():
            if prop_name == "material_color":
                # Create and assign material
                mat = bpy.data.materials.new(name=f"{name}_Material")
                try:
                    if hasattr(mat, 'use_nodes'):
                        mat.use_nodes = True
                except (AttributeError, TypeError):
                    # use_nodes may not be available in newer Blender versions
                    pass
                
                bsdf = mat.node_tree.nodes.get('Principled BSDF')
                if bsdf:
                    bsdf.inputs['Base Color'].default_value = prop_value
                
                if obj.data and hasattr(obj.data, 'materials'):
                    obj.data.materials.append(mat)
            elif prop_name == "roughness":
                if obj.data and hasattr(obj.data, 'materials') and obj.data.materials:
                    try:
                        bsdf = obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
                        if bsdf:
                            bsdf.inputs['Roughness'].default_value = prop_value
                    except (AttributeError, TypeError):
                        pass
            else:
                # Store as custom property
                try:
                    obj[prop_name] = prop_value
                except (AttributeError, TypeError):
                    pass
    
    return obj


def load_assets(config=None, clear_existing=False):
    """
    Load all assets defined in the configuration
    
    Args:
        config (dict): Asset configuration dictionary (uses ASSETS_CONFIG if None)
        clear_existing (bool): If True, clear all objects before loading assets
    
    Returns:
        list: List of created/imported objects
    """
    import bpy
    
    if config is None:
        config = ASSETS_CONFIG
    
    if clear_existing:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
    
    loaded_objects = []
    
    for asset_config in config.get("assets", []):
        if not asset_config.get("enabled", True):
            continue
        
        print(f"Loading asset: {asset_config.get('name', 'Unknown')}")
        obj = create_custom_object(asset_config)
        
        if obj:
            loaded_objects.append(obj)
            print(f"✓ Successfully loaded: {obj.name}")
        else:
            print(f"✗ Failed to load: {asset_config.get('name', 'Unknown')}")
    
    return loaded_objects


if __name__ == "__main__":
    # This allows running the script directly from Blender
    import bpy
    load_assets(clear_existing=False)
    print(f"\nLoaded {len(load_assets())} assets")
