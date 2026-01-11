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


def create_box(position, size, color, index):
    """Create a single box at specified position"""
    # Create cube
    bpy.ops.mesh.primitive_cube_add(location=position)
    box = bpy.context.active_object
    box.name = f"Box_{index:03d}"

    # Scale to box size
    box.scale = (size / 2, size / 2, size / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Create material with unique color
    mat = bpy.data.materials.new(name=f"Box_Material_{index:03d}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')

    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.4
    bsdf.inputs['Metallic'].default_value = 0.1

    box.data.materials.append(mat)

    return box


def generate_random_color():
    """Generate a random bright color for box identification"""
    # Generate saturated colors for better visibility
    hue = random.random()
    saturation = random.uniform(0.6, 1.0)
    value = random.uniform(0.5, 1.0)

    # Convert HSV to RGB
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)

    return (r, g, b, 1.0)


def create_boxes_on_conveyor(config, conveyor):
    """Create randomly positioned boxes on the conveyor belt

    Boxes can overlap - later boxes will appear on top of earlier ones
    to prevent rendering artifacts (black holes)
    """
    conv_config = config['conveyor']
    box_config = config['boxes']

    length = conv_config['length']
    width = conv_config['width']
    thickness = conv_config['thickness']
    box_size = box_config['size']

    # Set random seed if specified
    if box_config['random_seed'] is not None:
        random.seed(box_config['random_seed'])

    # Generate random number of boxes
    num_boxes = random.randint(box_config['min_count'], box_config['max_count'])

    boxes = []

    # Calculate safe placement boundaries
    # Boxes should be fully on the belt
    x_min = -length / 2 + box_size / 2
    x_max = length / 2 - box_size / 2
    y_min = -width / 2 + box_size / 2
    y_max = width / 2 - box_size / 2
    base_z_position = thickness / 2 + box_size / 2  # On top of conveyor

    # Z-offset for each box - later boxes slightly higher
    # This ensures that overlapping boxes render correctly
    z_offset_per_box = box_config.get('z_layer_offset', 0.0001)  # 0.1mm per box

    for i in range(num_boxes):
        # Random position on conveyor
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)

        # Each subsequent box is slightly higher to prevent Z-fighting
        z_position = base_z_position + (i * z_offset_per_box)
        position = (x, y, z_position)

        # Generate color
        if box_config['random_colors']:
            color = generate_random_color()
        else:
            color = (0.8, 0.2, 0.2, 1.0)  # Default red

        box = create_box(position, box_size, color, i)
        boxes.append(box)

        # Parent box to conveyor so they move together
        box.parent = conveyor

    print(f"Created {num_boxes} boxes on conveyor")
    print(f"  Boxes can overlap - later boxes appear on top")

    return boxes


def setup_world_background():
    """Setup a neutral world background"""
    world = bpy.data.worlds['World']
    world.use_nodes = True

    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1.0)
        bg_node.inputs['Strength'].default_value = 0.2
