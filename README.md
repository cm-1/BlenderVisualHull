## TODO

Links on using third-party modules in Blender Addons:

 * Official addons for comparison: https://developer.blender.org/diffusion/BA/browse/master/
 * Comprehensive overview: https://blender.stackexchange.com/a/181953
   * SUPER comprehensive overview, worth _eventually_ implementing something similar to: https://github.com/robertguetzkow/blender-python-examples/tree/master/add_ons/install_dependencies
 * Shell commands: https://blender.stackexchange.com/a/122337
 * Simple Python code: https://blender.stackexchange.com/a/139720
 * https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/
 * On shortcut for reloading and stuff: https://web.archive.org/web/20210314173702/https://developer.blender.org/T67387



## Multi-File Notes

**NEED TO UPDATE THIS SECTION! I CHANGED `__init__.py` SINCE I WROTE THIS!**

My Current Quick Process For Multi-File Add-Ons:

Create a .zip file that, within it, has a folder with the same name, and then the __init__.py and whatnot.

So, for example, a structure looking like:

 * `MyAddonName.zip`
    * `MyAddonName` (directory)
        * `__init__.py`
        * `somethingElse.py`
        * ...

And then install it from Blender. For me, on Windows, the code will now appear somewhere like `C:\Users\U1\AppData\Roaming\Blender Foundation\Blender\2.92\scripts\addons\VisHullAddon`. Such a folder could probably just created manually, but I'm not 100% sure about this and, at the time of this writing, I don't want to look into it to verify for sure (though this is something I should check someday in the future).

Then I start working on the code here. To reload the scripts, you can press F3 and search for "Reload Scripts" or find it in the menu, which is the tiny Blender logo to the _left_ of File, followed by System, followed by Reload Scripts, but for this project, I'm finding it faster to just have a scripting view open and, inside of it, having the next tiny bit of code in its own Python file that I can just run with the click of the play button or Alt + P:
```python
import bpy

bpy.ops.script.reload()
```

A bit faster than typing something each time or navigating through a menu each time. You can also apparently setup a shortcut for this (see [here](https://web.archive.org/web/20210314173702/https://developer.blender.org/T67387)). It used to have a shortcut, F8, before Blender 2.8.

Of course, when working with multiple files in a Blender add-on, you'll also want some custom stuff within `__init__.py` before the "normal" imports, so that changes to the non-`__init__.py` files will be reloaded with the `bpy.ops.script.reload()` call above. Imagine your addon has the following file structure:

 * `MyAddonName` (directory)
    * `__init__.py`
    * `myFirstModule.py`

```python
if "bpy" in locals():
    import importlib
    importlib.reload(myFirstModule)
    ...

from .myFirstModule import MyClass
```

The above technique (or, at least, similar) can even be seen in [official addons](https://web.archive.org/web/20210402214355/https://developer.blender.org/diffusion/BA/browse/master/add_curve_extra_objects/__init__.py). I don't do it exactly the same, though, so there might be nuances where the linked version is possibly better. Additionally, the discussion [here](https://web.archive.org/web/20210314173702/https://developer.blender.org/T67387) might also be worth looking at for what to do differently if I encounter issues with my current method in the future.

One final thing to note is that, for convenience, I am keeping my modules in a dictionary to pair them with string names, for debugging purposes, as seen below.

```python
myOwnModules = {
    'importTest': importTest
}
if "bpy" in locals():
    import importlib
    for moduleName, module in myOwnModules.items():
        print("Reinstalling:", moduleName)
        importlib.reload(module)

```

Commands for installing pyclipper. See other stuff to see where you need to `cd` to before running these.
```
./python -m ensurepip
./python -m pip install --upgrade pip
./python -m pip install pyclipper
```
