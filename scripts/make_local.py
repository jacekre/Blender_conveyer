"""
Make Linked Objects Local
Use this to convert packed/linked mesh data to local editable objects.

Run this in Blender (Scripting workspace) while your .blend file is open.
"""

import bpy


def make_all_local():
    """Convert all linked objects and data to local"""
    
    print("\n" + "="*80)
    print("Making all linked data local...")
    print("="*80 + "\n")
    
    # Method 1: Make all objects local
    for obj in bpy.data.objects:
        if obj.library:
            print(f"Making object local: {obj.name}")
            # This will convert the object to local
            bpy.ops.object.make_local(type='SELECT_OBDATA')
    
    # Method 2: Make all mesh data local
    for mesh in bpy.data.meshes:
        if mesh.is_library_indirect or mesh.library:
            print(f"Making mesh local: {mesh.name}")
            mesh.make_local()
    
    # Method 3: Unpack all packed files
    for image in bpy.data.images:
        if image.packed_file:
            print(f"Unpacking image: {image.name}")
            image.unpack()
    
    print("\n" + "="*80)
    print("Done! All data is now local and editable.")
    print("="*80 + "\n")


def make_object_local_by_name(obj_name):
    """Make a specific object local by name"""
    
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"Object not found: {obj_name}")
        return False
    
    if obj.library:
        print(f"Making object local: {obj_name}")
        # Select the object first
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Make local with all data
        bpy.ops.object.make_local(type='SELECT_OBDATA')
        print(f"✓ Successfully made {obj_name} local")
        return True
    else:
        print(f"Object is already local: {obj_name}")
        return False


def unpack_all_files():
    """Unpack all packed files"""
    
    print("\nUnpacking all packed files...")
    
    for image in bpy.data.images:
        if image.packed_file:
            print(f"Unpacking: {image.name}")
            image.unpack()
    
    for sound in bpy.data.sounds:
        if sound.packed_file:
            print(f"Unpacking: {sound.name}")
            sound.unpack()
    
    print("Done unpacking!\n")


if __name__ == "__main__":
    # Uncomment the function you want to use:
    
    # Option 1: Make everything local (safest)
    make_all_local()
    
    # Option 2: Unpack all files
    # unpack_all_files()
    
    # Option 3: Make specific object local
    # make_object_local_by_name("TinFoil_A.002")
    
    # Save the file
    print("\nSaving file...")
    bpy.ops.wm.save_mainfile()
    print("✓ File saved!")
