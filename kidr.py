#
# KIDR: Kerberos Interactive Data Renamer (v6.0.0 - Definitive)
#
# This add-on provides a tool to batch rename the data-blocks of selected
# objects to match their respective object names. It is engineered for
# performance and stability, using direct API access and handling edge
# cases such as multi-user data and objects without data-blocks.
#

bl_info = {
    "name": "Kerberos Interactive Data Renamer",
    "author": "Derjyn",
    "version": (1, 6, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Object > Rename Data to Object Name | Shortcut: Ctrl+Alt+R",
    "description": "Batch renames data-blocks of selected objects to match.",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy

# Define the operator's ID name as a constant to prevent typos.
OPERATOR_IDNAME = "object.rename_data_to_object"


class OBJECT_OT_rename_data_to_object(bpy.types.Operator):
    """Rename object data-blocks to match the object's name"""
    bl_idname = OPERATOR_IDNAME
    bl_label = "Rename Data to Object Name"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # This safety check ensures the operator is only active when
        # in Object Mode with at least one object selected.
        return context.mode == 'OBJECT' and context.selected_objects

    def execute(self, context):
        renamed_count = 0
        skipped_count = 0
        
        # This loop is highly optimized for performance by using direct data access
        # and avoiding slow Blender operators (`bpy.ops`).
        for obj in context.selected_objects:
            # Skip objects with no data (like Empties) or multi-user data.
            if not obj.data or (obj.data.users > 1 and obj.data.name != obj.name):
                skipped_count += 1
                continue
            # Rename only if the names don't already match.
            if obj.data.name != obj.name:
                obj.data.name = obj.name
                renamed_count += 1

        self.report({'INFO'}, f"Renamed data for {renamed_count} object(s). Skipped {skipped_count}.")
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(OPERATOR_IDNAME)


def register():
    # 1. Register the Operator Class
    bpy.utils.register_class(OBJECT_OT_rename_data_to_object)
    
    # 2. Add the Menu Item
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # 3. Add the Keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    km = kc.keymaps.get('Object Mode')
    if km:
        km.keymap_items.new(OPERATOR_IDNAME, 'R', 'PRESS', ctrl=True, alt=True)


def unregister():
    # 1. Remove the Keymap
    # This method is highly robust. It actively searches for the keymap item
    # instead of relying on a stored variable, which prevents all errors
    # related to script reloading.
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    km = kc.keymaps.get('Object Mode')
    if km:
        for kmi in km.keymap_items:
            if kmi.idname == OPERATOR_IDNAME:
                km.keymap_items.remove(kmi)
                break
    
    # 2. Remove the Menu Item
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    
    # 3. Unregister the Operator Class
    bpy.utils.unregister_class(OBJECT_OT_rename_data_to_object)