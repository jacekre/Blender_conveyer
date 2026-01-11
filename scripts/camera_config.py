import bpy
import math
from mathutils import Vector


def setup_camera(config):
    """Setup camera to view the conveyor belt from above"""
    cam_config = config['camera']
    conv_config = config['conveyor']

    # Camera parameters
    height = cam_config['height']
    res_x = cam_config['resolution_x']
    res_y = cam_config['resolution_y']
    look_at_height = cam_config['look_at_height']

    # Conveyor dimensions
    conveyor_width = conv_config['width']

    # Create camera
    bpy.ops.object.camera_add(location=(0, 0, height))
    camera = bpy.context.active_object
    camera.name = "Conveyor_Camera"

    # Point camera straight down at conveyor center
    camera.rotation_euler = (0, 0, 0)  # Will be set by constraint

    # Set as active camera
    bpy.context.scene.camera = camera

    # Add Track To constraint to look at conveyor
    constraint = camera.constraints.new(type='TRACK_TO')

    # Create empty at conveyor center to track
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, look_at_height))
    target = bpy.context.active_object
    target.name = "Camera_Target"

    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    # Calculate camera FOV
    # We want the camera to see the full width of the conveyor
    # At height h, to see width w: FOV = 2 * atan(w / (2 * h))

    distance_to_target = height - look_at_height
    horizontal_fov = 2 * math.atan(conveyor_width / (2 * distance_to_target))

    # Blender uses vertical FOV, convert from horizontal
    aspect_ratio = res_x / res_y
    vertical_fov = 2 * math.atan(math.tan(horizontal_fov / 2) / aspect_ratio)

    # Set camera properties
    camera.data.lens_unit = 'FOV'
    camera.data.angle = vertical_fov

    # Calculate the viewing area dimensions
    view_width = conveyor_width
    view_height = view_width / aspect_ratio

    print(f"Camera setup:")
    print(f"  Position: (0, 0, {height}m)")
    print(f"  Viewing area: {view_width:.3f}m x {view_height:.3f}m")
    print(f"  Horizontal FOV: {math.degrees(horizontal_fov):.2f}°")
    print(f"  Vertical FOV: {math.degrees(vertical_fov):.2f}°")
    print(f"  Resolution: {res_x}x{res_y}px")

    # Set render resolution
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.context.scene.render.resolution_percentage = 100

    return camera, target, view_height


def setup_render_settings(config):
    """Configure render engine and output settings"""
    render_config = config['render']

    scene = bpy.context.scene

    # Set render engine
    engine = render_config.get('engine', 'CYCLES')
    scene.render.engine = engine

    if engine == 'CYCLES':
        scene.cycles.samples = render_config.get('samples', 64)
        scene.cycles.use_denoising = render_config.get('use_denoising', True)

        # Use GPU if available
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
        bpy.context.scene.cycles.device = 'GPU'

    # Set output format
    scene.render.image_settings.file_format = render_config.get('file_format', 'PNG')
    scene.render.image_settings.color_mode = 'RGB'

    # Film settings for better quality
    if hasattr(scene.render, 'film_transparent'):
        scene.render.film_transparent = False

    print(f"Render settings: {engine}, {render_config.get('samples', 64)} samples")
