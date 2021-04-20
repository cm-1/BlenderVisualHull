# Fill out more fields here later.
# See:
#   https://blenderartists.org/t/addons-clean-up-your-bl-info/664876
#   https://wiki.blender.org/wiki/Process/Addons/Guidelines/metainfo

bl_info = {
    "name": "Visual Hull Generation",
    "blender": (2, 80, 0),
    "category": "Mesh",
}

# List of modules with their string names.
myOwnModules = {
    'importTest': importTest
}
# Reloading of modules so that changes to files other than
# the __init__.py file are recognized/used.
# Has to be done before the "normal" import calls later.
# This seems to roughly be the way it's done for official addons, e.g., 
# https://developer.blender.org/diffusion/BA/browse/master/add_curve_extra_objects/__init__.py
# (The page has also been web archived for future reference. 2021-04-02)
if "bpy" in locals():
    import importlib
    for moduleName, module in myOwnModules.items():
        print("Reinstalling:", moduleName)
        importlib.reload(module)
else:
    print("bpy not in locals, so no doing module reloads!") 

# -----------------------------------------------
# -----------------------------------------------
# -----------------------------------------------
# -----------------------------------------------
# -----------------------------------------------

# Now, the "normal" imports
import bpy
from .importTest import PointCreator



class ObjectCursorArray(bpy.types.Operator):
    """Object Cursor Array"""
    bl_idname = "object.cursor_array"
    bl_label = "Cursor Array"
    bl_options = {'REGISTER', 'UNDO'}
    
    # moved assignment from execute() to the body of the class...
    total: bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self, context):
        pc = PointCreator(self.total)
        scene = context.scene
        cursor = scene.cursor.location
        obj = context.active_object

        points = pc.getPoints(-50, 50, 100)

        for pt in points:
            obj_new = obj.copy()
            scene.collection.objects.link(obj_new)

            obj_new.location = (pt[0], pt[1], 1)

        return {'FINISHED'}
    

def menu_func(self, context):
    self.layout.operator(ObjectCursorArray.bl_idname)

def register():
    bpy.utils.register_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()