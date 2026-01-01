bl_info = {
    "name": "DoubleYou LOD Tools",
    "author": "DoubleYou",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > DoubleYou",
    "description": "Tools to help create LOD models.",
    "category": "Object",
}

import bpy
from . import doubleyou_lod_tools


def register():
    doubleyou_lod_tools.register()


def unregister():
    doubleyou_lod_tools.unregister()


if __name__ == "__main__":
    register()