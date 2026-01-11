import bpy
import math
from mathutils import Vector


def setup_lighting(config):
    """Setup area light strip at 45 degree angle above conveyor

    Light strip is perpendicular to conveyor movement direction (along Y axis)
    """
    light_config = config['lighting']
    conv_config = config['conveyor']

    angle_deg = light_config['angle_degrees']
    angle_rad = math.radians(angle_deg)
    distance = light_config['distance_from_conveyor']
    strength = light_config['strength']
    light_size = light_config['size']

    conveyor_length = conv_config['length']
    conveyor_width = conv_config['width']

    # Calculate light position
    # Light is at angle from horizontal, distance away from center
    # Position along X axis at angle (perpendicular to conveyor movement)
    x_offset = distance * math.cos(angle_rad)
    z_height = distance * math.sin(angle_rad)

    # Position light strip perpendicular to conveyor movement (along Y axis)
    light_position = (-x_offset, 0, z_height)

    # Create area light
    bpy.ops.object.light_add(type='AREA', location=light_position)
    light = bpy.context.active_object
    light.name = "Light_Strip"

    # Configure light properties
    light_data = light.data
    light_data.energy = strength
    light_data.shape = 'RECTANGLE'

    # Make light strip cover the conveyor width (perpendicular to movement)
    light_data.size = conveyor_width * 0.9  # Cover width
    light_data.size_y = 0.2  # Narrow strip

    # Use Track To constraint to ensure light points at conveyor
    # This is more reliable than manual rotation
    constraint = light.constraints.new(type='TRACK_TO')

    # Create target at conveyor center
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0.05))
    target = bpy.context.active_object
    target.name = "Light_Target"

    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    print(f"  Light oriented perpendicular to movement direction (along Y axis)")

    print(f"Lighting setup:")
    print(f"  Type: Area light strip")
    print(f"  Position: ({light_position[0]:.2f}, {light_position[1]:.2f}, {light_position[2]:.2f})")
    print(f"  Angle: {angle_deg}°")
    print(f"  Strength: {strength}W")
    print(f"  Size: {light_data.size:.2f}m x {light_data.size_y:.2f}m")

    return light


def add_fill_lights(config):
    """Add subtle fill lights for better visibility (optional)"""
    conv_config = config['conveyor']
    conveyor_width = conv_config['width']

    # Add weak fill light from opposite side to reduce harsh shadows
    # Also perpendicular to movement direction
    bpy.ops.object.light_add(type='AREA', location=(0.8, 0, 0.8))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"

    fill_data = fill_light.data
    fill_data.energy = 20  # Much weaker than main light
    fill_data.shape = 'RECTANGLE'
    fill_data.size = conveyor_width * 0.7
    fill_data.size_y = 0.3

    # Use Track To constraint to point at conveyor (same target as main light)
    constraint = fill_light.constraints.new(type='TRACK_TO')

    # Use the same target as main light (Light_Target)
    target = bpy.data.objects.get("Light_Target")
    if target:
        constraint.target = target
    else:
        # Create new target if it doesn't exist
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0.05))
        target = bpy.context.active_object
        target.name = "Fill_Light_Target"
        constraint.target = target

    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    print("  Added fill light for softer shadows (pointing at conveyor)")

    return fill_light
