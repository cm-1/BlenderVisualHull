# Fill out more fields here later.
# See:
#   https://blenderartists.org/t/addons-clean-up-your-bl-info/664876
#   https://wiki.blender.org/wiki/Process/Addons/Guidelines/metainfo

bl_info = {
    "name": "Visual Hull Generation",
    "blender": (2, 80, 0),
    "category": "Mesh",
}


# Reloading of modules so that changes to files other than
# the __init__.py file are recognized/used.
# Has to be done before the "normal" import calls later.
# This seems to roughly be the way it's done for official addons, e.g., 
# https://developer.blender.org/diffusion/BA/browse/master/add_curve_extra_objects/__init__.py
# (The page has also been web archived for future reference. 2021-04-02)
if "bpy" in locals():
    # List of modules with their string names.
    # ORDER MATTERS!
    # Suppose A imports B
    # If we reload A before B here, then A will not have B's newest changes in it. 
    # So, we need to reload some modules before the other modules that depend on them.
    myOwnModules = {
        'rbt': rbt,
        'visHullTwoD': visHullTwoD,
        'importTest': importTest,
        'sceneCreation2D': sceneCreation2D
    }
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
from .sceneCreation2D import SceneCreator2D



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

class ObjectSceneCreation2D(bpy.types.Operator):
    """Object 2D Scene Creator"""
    bl_idname = "object.scene_creation_two_dimensional"
    bl_label = "Scene 2D"
    bl_options = {'REGISTER', 'UNDO'}
    
    # moved assignment from execute() to the body of the class...
    sceneNum: bpy.props.IntProperty(name="Scene Number", default=5, min=0, max=6)

    def execute(self, context):
        sc = SceneCreator2D(self.sceneNum)
        sc.createScene()

        return {'FINISHED'}  

def menu_func_cursor(self, context):
    self.layout.operator(ObjectCursorArray.bl_idname)

def menu_func_scene_2D(self, context):
    self.layout.operator(ObjectSceneCreation2D.bl_idname)

def register():
    bpy.utils.register_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.append(menu_func_cursor)

    bpy.utils.register_class(ObjectSceneCreation2D)
    bpy.types.VIEW3D_MT_add.append(menu_func_scene_2D)

def unregister():
    bpy.utils.unregister_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.remove(menu_func_cursor)

    bpy.utils.unregister_class(ObjectSceneCreation2D)
    bpy.types.VIEW3D_MT_add.remove(menu_func_scene_2D)


if __name__ == "__main__":
    register()