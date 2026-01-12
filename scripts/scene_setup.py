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


def create_sphere(position, diameter, color, density, index):
    """Create a single translucent sphere at specified position with variable density

    Args:
        position: (x, y, z) tuple for sphere location
        diameter: sphere diameter in meters
        color: RGBA color tuple
        density: material density (0.0-1.0) - affects translucency
        index: sphere index for naming
    """
    # Create UV sphere (default diameter is 2.0)
    bpy.ops.mesh.primitive_uv_sphere_add(location=position, radius=diameter/2)
    sphere = bpy.context.active_object
    sphere.name = f"Sphere_{index:03d}"

    # Create translucent glass-like material
    mat = bpy.data.materials.new(name=f"Sphere_Material_{index:03d}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')

    # Map density to transmission: lower density = higher transmission (more transparent)
    # density 0.0 -> transmission 1.0 (fully transparent)
    # density 1.0 -> transmission 0.0 (opaque)
    transmission = 1.0 - density

    # Adjust IOR based on density (denser materials often have higher IOR)
    ior = 1.33 + (density * 0.25)  # Range: 1.33 (water-like) to 1.58 (dense glass)

    # Translucent colored glass material with density-based properties
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Transmission'].default_value = transmission
    bsdf.inputs['Roughness'].default_value = 0.05      # Smooth surface
    bsdf.inputs['IOR'].default_value = ior
    bsdf.inputs['Alpha'].default_value = max(0.5, 1.0 - density * 0.5)  # Denser = more opaque

    # Enable blend mode for transparency
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'HASHED'

    sphere.data.materials.append(mat)

    # Store density as custom property for reference
    sphere["density"] = density

    return sphere


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

    # Generate random number of spheres
    num_spheres = random.randint(box_config['min_count'], box_config['max_count'])

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

    for i in range(num_spheres):
        # Random position on conveyor
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)

        # Each subsequent sphere is slightly higher to prevent Z-fighting
        z_position = base_z_position + (i * z_offset_per_sphere)
        position = (x, y, z_position)

        # Generate color
        if box_config['random_colors']:
            color = generate_random_color()
        else:
            color = (0.8, 0.2, 0.2, 1.0)  # Default red

        # Generate random density for this sphere
        density = random.uniform(density_min, density_max)

        sphere = create_sphere(position, sphere_diameter, color, density, i)
        spheres.append(sphere)

        # Parent sphere to conveyor so they move together
        sphere.parent = conveyor

    print(f"Created {num_spheres} translucent spheres on conveyor")
    print(f"  Density range: {density_min:.2f} to {density_max:.2f}")
    print(f"  Spheres can overlap - later spheres appear on top")

    return spheres


def setup_world_background():
    """Setup a neutral world background"""
    world = bpy.data.worlds['World']
    world.use_nodes = True

    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)
        bg_node.inputs['Strength'].default_value = 0.2
