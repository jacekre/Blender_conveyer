import bpy
import random
from mathutils import Vector


def clear_scene():
    """Remove all mesh objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Remove all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)


def create_conveyor_belt(config):
    """Create the conveyor belt mesh"""
    conv_config = config['conveyor']
    length = conv_config['length']
    width = conv_config['width']
    thickness = conv_config['thickness']

    # Create cube and scale it to conveyor dimensions
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    conveyor = bpy.context.active_object
    conveyor.name = "Conveyor_Belt"

    # Scale to proper dimensions
    conveyor.scale = (length / 2, width / 2, thickness / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Create material
    mat = bpy.data.materials.new(name="Conveyor_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')

    color = conv_config['material_color']
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.7

    conveyor.data.materials.append(mat)

    return conveyor


def create_sphere(position, diameter, material_type, density, index, wall_thickness=0.0003):
    """Create a single translucent hollow sphere with wall thickness (realistic PET bottle)

    Uses scientifically accurate PET plastic optical properties:
    - IOR: 1.575 (measured at 589nm, RefractiveIndex.INFO)
    - Transmission: 86-88% base (GB/T 16958 standard)
    - Roughness: 0.01-0.015 (SPI Grade A finish)
    - Hollow geometry: 0.2-0.4mm wall thickness (typical PET bottles)

    Args:
        position: (x, y, z) tuple for sphere location
        diameter: sphere diameter in meters
        material_type: PET material type (PET-Clear, PET-Greenish, PET-Bluish) or "random"
        density: material density (0.0-1.0) - affects transmission (wall thickness)
        index: sphere index for naming
        wall_thickness: wall thickness in meters (default 0.0003m = 0.3mm)
    """
    # Create UV sphere (default diameter is 2.0)
    bpy.ops.mesh.primitive_uv_sphere_add(location=position, radius=diameter/2)
    sphere = bpy.context.active_object
    sphere.name = f"Sphere_{index:03d}"

    # Add Solidify modifier to create hollow sphere with wall thickness
    # Real PET bottles have walls ~0.2-0.4mm thick (configurable)
    #
    # CRITICAL for correct refraction:
    # - Outer surface normals: pointing OUTWARD (default from UV sphere)
    # - Inner surface normals: pointing INWARD (into hollow interior)
    # - offset = -1.0: thickness grows INWARD, keeps outer surface unchanged
    #
    solidify = sphere.modifiers.new(name="Hollow_Wall", type='SOLIDIFY')
    solidify.thickness = wall_thickness  # From config (default 0.0003m = 0.3mm)
    solidify.offset = -1.0  # Grow INWARD only (outer surface unchanged, inner created inside)
    solidify.use_even_offset = True  # Better geometry for curved surfaces
    solidify.use_quality_normals = True  # Better shading on curved surfaces
    solidify.use_rim = False  # UV sphere is closed, no holes to fill
    solidify.use_flip_normals = False  # Keep default: outer normals OUT, inner normals IN

    # Apply the modifier to make geometry permanent
    bpy.context.view_layer.objects.active = sphere
    bpy.ops.object.modifier_apply(modifier="Hollow_Wall")

    # Note: With offset=-1.0 and flip_normals=False, Solidify creates:
    # - Outer surface: normals pointing OUTWARD (unchanged original)
    # - Inner surface: normals pointing INWARD (to hollow interior)
    # This is correct for transparent hollow objects like glass/plastic bottles
    #
    # DO NOT run normals_make_consistent here - it would flip inner normals wrong!

    # Create translucent glass-like material
    mat = bpy.data.materials.new(name=f"Sphere_Material_{index:03d}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')

    # Debug: Print available inputs on first sphere
    if index == 0:
        print(f"\n  Principled BSDF available inputs: {[inp.name for inp in bsdf.inputs][:10]}...")
        print(f"  Material type: {material_type}")

    # Get material properties
    if material_type == "random":
        color = generate_random_color()
        roughness = 0.05
        ior = 1.33 + (density * 0.25)  # Range: 1.33 (water-like) to 1.58 (dense glass)
        # Random materials: density strongly affects transmission
        transmission = 1.0 - density  # 0.0 density = fully transparent, 1.0 = opaque
    else:
        props = get_pet_material_properties(material_type)
        color = props["color"]
        roughness = props["roughness"]
        ior = props["ior"]
        base_transmission = props["base_transmission"]

        # PET materials: always highly transparent, density only slightly reduces it
        # Density represents plastic wall thickness (thicker walls = less transmission)
        # Formula: base_transmission * (1.0 - density * 0.2)
        #
        # Examples with PET-Clear (base 88%):
        #   density 0.3 (thin walls)  -> transmission ~86% (88% * 0.94)
        #   density 0.6 (normal walls) -> transmission ~79% (88% * 0.88)
        #   density 0.9 (thick walls)  -> transmission ~72% (88% * 0.82)
        #
        # This matches real PET bottles: 85-90% for thin/clear bottles,
        # lower for thicker or tinted bottles
        transmission = base_transmission * (1.0 - density * 0.2)

    # Debug: Print material properties on first sphere
    if index == 0:
        if material_type != "random":
            props = get_pet_material_properties(material_type)
            print(f"  {props['description']}")
        print(f"\n  Geometry (Hollow PET Bottle):")
        print(f"    - Wall thickness: {wall_thickness*1000:.2f}mm")
        print(f"    - Outer surface: normals pointing OUTWARD")
        print(f"    - Inner surface: normals pointing INWARD (to hollow interior)")
        print(f"    - Both surfaces rendered (backface culling OFF)")
        print(f"\n  Material Properties:")
        print(f"    - Color RGB: {color[:3]}")
        print(f"    - Roughness: {roughness:.3f} (SPI Grade A finish)")
        print(f"    - IOR: {ior} (PET at 589nm)")
        print(f"    - Transmission: {transmission:.3f} ({transmission*100:.1f}%)")
        print(f"    - Density: {density:.2f} (wall thickness variation)")

    # Translucent colored glass material with density-based properties
    # Blender 5.0 compatibility: Handle different input names

    # Set Base Color
    if 'Base Color' in bsdf.inputs:
        bsdf.inputs['Base Color'].default_value = color

    # CRITICAL: Set Metallic to 0 for transparent plastic materials
    if 'Metallic' in bsdf.inputs:
        bsdf.inputs['Metallic'].default_value = 0.0

    # Set Specular for plastic look
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.5

    # Set roughness (smooth plastic surface)
    if 'Roughness' in bsdf.inputs:
        bsdf.inputs['Roughness'].default_value = roughness

    # Set IOR (critical for refraction through transparent material)
    if 'IOR' in bsdf.inputs:
        bsdf.inputs['IOR'].default_value = ior

    # Try Blender 5.0 name first, fallback to older version
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = transmission
        if index == 0:
            print(f"  Using 'Transmission Weight' input (Blender 5.0)")
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = transmission
        if index == 0:
            print(f"  Using 'Transmission' input (Blender <5.0)")
    else:
        if index == 0:
            print(f"  WARNING: No transmission input found - spheres may not be translucent!")

    # Set Transmission Roughness to 0 (smooth transparent surface, no frosted glass effect)
    if 'Transmission Roughness' in bsdf.inputs:
        bsdf.inputs['Transmission Roughness'].default_value = 0.0

    # Handle Alpha/Opacity (should be 1.0 - transmission handles the transparency)
    if 'Alpha' in bsdf.inputs:
        bsdf.inputs['Alpha'].default_value = 1.0  # Solid object, transmission creates transparency

    # Enable blend mode for transparency - Blender 5.0 compatibility
    if hasattr(mat, 'blend_method'):
        mat.blend_method = 'BLEND'
    else:
        if index == 0:
            print(f"  WARNING: blend_method not available (Blender 5.0 API change)")

    # Shadow method - Blender 5.0 compatibility
    if hasattr(mat, 'shadow_method'):
        mat.shadow_method = 'HASHED'
    else:
        if index == 0:
            print(f"  Note: shadow_method not available (Blender 5.0 - transparency will still work)")

    # CRITICAL: Enable backface culling OFF for hollow objects
    # Hollow spheres need to render BOTH outer and inner surfaces
    # Default Cycles culling would hide inner surface (backfaces)
    if hasattr(mat, 'use_backface_culling'):
        mat.use_backface_culling = False  # Render both sides
        if index == 0:
            print(f"  Backface culling: OFF (renders inner surface)")
    else:
        if index == 0:
            print(f"  Note: use_backface_culling not available")

    sphere.data.materials.append(mat)

    # Store material info as custom properties for reference
    sphere["density"] = density
    sphere["material_type"] = material_type

    return sphere


def get_pet_material_properties(material_type):
    """Return color and properties for PET plastic bottle materials

    PET bottles are highly transparent with subtle color tints.
    These properties are based on scientific research and measurements.

    Scientific basis:
    - IOR: 1.575 (measured at 589nm yellow sodium D-line, RefractiveIndex.INFO)
    - Transmission: 85-90% typical for PET bottles (GB/T 16958 standard)
    - Roughness: SPI Grade A finish (0.012-0.4 μm Ra) for glossy bottles
    - Color additives reduce transmission slightly

    Args:
        material_type: Type of PET material (PET-Clear, PET-Greenish, PET-Bluish)

    Returns:
        Dictionary with color, roughness, ior, and base_transmission properties
    """
    properties = {
        "PET-Clear": {
            "color": (1.0, 1.0, 1.0, 1.0),  # Pure clear - no tint
            "roughness": 0.01,  # Very smooth plastic surface (SPI Grade A)
            "ior": 1.575,  # PET plastic IOR at 589nm (scientifically accurate)
            "base_transmission": 0.88,  # 88% transmission (realistic for clear PET)
            "description": "Clear PET - 88% base transmission, scientifically accurate"
        },
        "PET-Greenish": {
            "color": (0.85, 1.0, 0.88, 1.0),  # Subtle green tint (light greenish)
            "roughness": 0.015,  # Slightly less smooth due to additives
            "ior": 1.575,  # Same IOR (color additives don't significantly change it)
            "base_transmission": 0.86,  # 86% transmission (color additives reduce slightly)
            "description": "Green-tinted PET - 86% base transmission"
        },
        "PET-Bluish": {
            "color": (0.88, 0.95, 1.0, 1.0),  # Subtle blue tint (light bluish)
            "roughness": 0.015,  # Slightly less smooth due to additives
            "ior": 1.575,  # Same IOR
            "base_transmission": 0.86,  # 86% transmission (color additives reduce slightly)
            "description": "Blue-tinted PET - 86% base transmission"
        }
    }
    return properties.get(material_type, properties["PET-Clear"])


def generate_random_color():
    """Generate a random bright color for sphere identification"""
    # Generate saturated colors for better visibility
    hue = random.random()
    saturation = random.uniform(0.6, 1.0)
    value = random.uniform(0.5, 1.0)

    # Convert HSV to RGB
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)

    return (r, g, b, 1.0)


def create_boxes_on_conveyor(config, conveyor):
    """Create randomly positioned translucent spheres on the conveyor belt

    Spheres can overlap - later spheres will appear on top of earlier ones
    to prevent rendering artifacts (black holes)
    """
    conv_config = config['conveyor']
    box_config = config['boxes']  # Keep variable name for config compatibility

    length = conv_config['length']
    width = conv_config['width']
    thickness = conv_config['thickness']
    sphere_diameter = box_config['size']  # Now interpreted as sphere diameter (0.1m)

    # Set random seed if specified
    if box_config['random_seed'] is not None:
        random.seed(box_config['random_seed'])

    # Calculate number of spheres based on spatial density or fixed count
    if box_config.get('use_spatial_density', False):
        # Calculate conveyor area (m²)
        conveyor_area = length * width

        # Get spatial density (spheres per m²)
        spatial_density = box_config.get('spatial_density', 10.0)
        density_variance = box_config.get('spatial_density_variance', 0.2)

        # Calculate base number of spheres
        base_count = conveyor_area * spatial_density

        # Add variance (e.g., ±20%)
        variance_factor = random.uniform(1.0 - density_variance, 1.0 + density_variance)
        num_spheres = max(1, int(base_count * variance_factor))

        print(f"  Using spatial density: {spatial_density:.1f} spheres/m²")
        print(f"  Conveyor area: {conveyor_area:.2f} m²")
        print(f"  Calculated sphere count: {num_spheres}")
    else:
        # Use fixed min/max count
        num_spheres = random.randint(box_config['min_count'], box_config['max_count'])
        print(f"  Using fixed count range: {box_config['min_count']}-{box_config['max_count']}")

    spheres = []

    # Calculate safe placement boundaries
    # Spheres should be fully on the belt
    sphere_radius = sphere_diameter / 2
    x_min = -length / 2 + sphere_radius
    x_max = length / 2 - sphere_radius
    y_min = -width / 2 + sphere_radius
    y_max = width / 2 - sphere_radius
    base_z_position = thickness / 2 + sphere_radius  # On top of conveyor

    # Z-offset for each sphere - later spheres slightly higher
    # This ensures that overlapping spheres render correctly
    z_offset_per_sphere = box_config.get('z_layer_offset', 0.0001)  # 0.1mm per sphere

    # Get density range from config
    density_min = box_config.get('density_min', 0.3)
    density_max = box_config.get('density_max', 0.9)

    # Get wall thickness from config (realistic PET bottle walls: 0.2-0.4mm)
    wall_thickness = box_config.get('wall_thickness', 0.0003)  # Default 0.3mm

    # Get material types from config
    material_types = box_config.get('material_types', ["PET-Clear", "PET-Greenish", "PET-Bluish"])
    use_random_colors = box_config.get('random_colors', False)

    # Count materials for statistics
    material_counts = {mat_type: 0 for mat_type in material_types}
    if use_random_colors:
        material_counts["random"] = 0

    for i in range(num_spheres):
        # Random position on conveyor
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)

        # Each subsequent sphere is slightly higher to prevent Z-fighting
        z_position = base_z_position + (i * z_offset_per_sphere)
        position = (x, y, z_position)

        # Select material type
        if use_random_colors:
            material_type = "random"
        else:
            material_type = random.choice(material_types)

        material_counts[material_type] += 1

        # Generate random density for this sphere
        density = random.uniform(density_min, density_max)

        sphere = create_sphere(position, sphere_diameter, material_type, density, i, wall_thickness)
        spheres.append(sphere)

        # Parent sphere to conveyor so they move together
        sphere.parent = conveyor

    # Calculate actual spatial density achieved
    actual_density = num_spheres / (length * width)

    print(f"\nCreated {num_spheres} translucent spheres on conveyor")
    print(f"  Actual spatial density: {actual_density:.1f} spheres/m²")
    print(f"  Material density range: {density_min:.2f} to {density_max:.2f}")
    print(f"  Material distribution: {material_counts}")

    # Calculate actual transmission range
    if not use_random_colors and material_types:
        example_mat = material_types[0]
        base_trans = get_pet_material_properties(example_mat)["base_transmission"]
        min_trans = base_trans * (1.0 - density_max * 0.2)
        max_trans = base_trans * (1.0 - density_min * 0.2)
        print(f"\n  PET Optical Properties (scientifically accurate):")
        print(f"    - Geometry: Hollow spheres with {wall_thickness*1000:.2f}mm wall thickness")
        print(f"    - IOR: 1.575 (measured at 589nm)")
        print(f"    - Base transmission: 86-88% (GB/T 16958 standard)")
        print(f"    - Final transmission range: {min_trans*100:.1f}%-{max_trans*100:.1f}% (after density adjustment)")
        print(f"    - Surface: SPI Grade A finish (Ra 0.01-0.015 roughness)")

    print(f"\n  Spheres can overlap - later spheres appear on top")
    print(f"\n  IMPORTANT: To see transparency in viewport:")
    print(f"    - Switch to 'Material Preview' mode (Z key → Material Preview)")
    print(f"    - Or 'Rendered' mode for full transparent effect")
    print(f"    - Solid mode won't show transparency correctly!")

    return spheres


def setup_world_background():
    """Setup a neutral world background"""
    world = bpy.data.worlds['World']
    world.use_nodes = True

    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)
        bg_node.inputs['Strength'].default_value = 0.2
