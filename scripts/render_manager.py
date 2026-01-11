import bpy
import os
from pathlib import Path


def setup_animation(config, conveyor):
    """Setup conveyor movement animation with discrete steps"""
    conv_config = config['conveyor']

    length = conv_config['length']
    step_size = conv_config['step_size']

    # Calculate number of steps for full conveyor length
    num_steps = int(length / step_size)

    print(f"\nAnimation setup:")
    print(f"  Conveyor length: {length}m")
    print(f"  Step size: {step_size}m")
    print(f"  Total steps: {num_steps}")

    # Set frame range
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = num_steps
    scene.frame_current = 1

    # Create keyframes for conveyor movement
    # Move along X axis in discrete steps
    for step in range(num_steps + 1):
        frame = step + 1
        x_position = -length / 2 + step * step_size

        # Set location
        conveyor.location.x = x_position

        # Insert keyframe
        conveyor.keyframe_insert(data_path="location", index=0, frame=frame)

    # Set interpolation to constant (step function, no smooth transitions)
    if conveyor.animation_data and conveyor.animation_data.action:
        for fcurve in conveyor.animation_data.action.fcurves:
            if fcurve.data_path == "location" and fcurve.array_index == 0:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'CONSTANT'

    print(f"  Animation frames: {scene.frame_start} to {scene.frame_end}")
    print(f"  Each frame = one step position")

    return num_steps


def render_sequence(config, output_folder="renders"):
    """Render the conveyor belt sequence, one frame per step"""
    scene = bpy.context.scene

    # Get project root directory
    blend_file_path = bpy.data.filepath
    if blend_file_path:
        project_root = str(Path(blend_file_path).parent)
    else:
        # If file not saved, use current working directory
        project_root = os.getcwd()

    # Setup output path
    output_path = os.path.join(project_root, output_folder)
    os.makedirs(output_path, exist_ok=True)

    # Get render settings
    render_config = config['render']
    file_format = render_config.get('file_format', 'PNG').lower()

    frame_start = scene.frame_start
    frame_end = scene.frame_end
    total_frames = frame_end - frame_start + 1

    print(f"\nStarting render sequence:")
    print(f"  Output folder: {output_path}")
    print(f"  Total frames to render: {total_frames}")
    print(f"  Format: {file_format.upper()}")

    # Render each frame
    for frame in range(frame_start, frame_end + 1):
        scene.frame_set(frame)

        # Set output filename
        filename = f"frame_{frame:04d}.{file_format}"
        filepath = os.path.join(output_path, filename)

        scene.render.filepath = filepath

        # Render
        print(f"  Rendering frame {frame}/{frame_end}... ", end="", flush=True)
        bpy.ops.render.render(write_still=True)
        print(f"Done -> {filename}")

    print(f"\nRender complete! {total_frames} images saved to: {output_path}")

    return output_path


def render_single_position(config, position_index, output_folder="renders"):
    """Render a single conveyor position"""
    scene = bpy.context.scene

    # Get project root directory
    blend_file_path = bpy.data.filepath
    if blend_file_path:
        project_root = str(Path(blend_file_path).parent)
    else:
        project_root = os.getcwd()

    # Setup output path
    output_path = os.path.join(project_root, output_folder)
    os.makedirs(output_path, exist_ok=True)

    # Get render settings
    render_config = config['render']
    file_format = render_config.get('file_format', 'PNG').lower()

    # Set frame and render
    frame = position_index + 1
    scene.frame_set(frame)

    filename = f"frame_{frame:04d}.{file_format}"
    filepath = os.path.join(output_path, filename)
    scene.render.filepath = filepath

    print(f"Rendering position {position_index} (frame {frame})...")
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {filepath}")

    return filepath


def preview_animation():
    """Play animation in viewport for preview"""
    print("\nPlaying animation preview in viewport...")
    print("Press ESC to stop playback")
    bpy.ops.screen.animation_play()
