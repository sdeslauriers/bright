from typing import Iterable

import glfw
import numpy as np
from OpenGL.GL import *

from bright.core import Camera
from bright.core import Renderer
from bright.mesh import Mesh
from bright.mesh import Renderer as MeshRenderer


def center(meshes: Iterable[Mesh]):
    """Returns the center of an iterable of meshes"""

    mins = np.min([np.min(mesh.vertices, axis=0) for mesh in meshes], axis=0)
    maxs = np.max([np.max(mesh.vertices, axis=0) for mesh in meshes], axis=0)

    return (maxs + mins) / 2


def render(renderers: Iterable[Renderer], start: int = 0, stop: int = 1):
    """Renders the renderables

    Renders all of the renderable objects in renderables to arrays. The
    output is a list of stop - start arrays each with a shape of
    (width, height, 3) where the third dimension is the RGB color.

    Args:
        renderers: An iterable that contains the renderers of the scene. Each
            item must be an instance of bright.Renderer.
        start: The first frame of the output list.
        stop: The last frame of the output list.

    Returns:
        frames: A list of arrays that each contain one frame of the output.

    """

    frames = []
    for frame_number in range(start, stop):

        for renderer in renderers:
            renderer.render()

        frames.append(renderer.frame.color)

    return frames


def _create_window(width, height):

    # Initialize the library
    if not glfw.init():
        return

    # Create a windowed mode window and its OpenGL context
    glfw.window_hint(glfw.VISIBLE, False)
    glfw.window_hint(glfw.FLOATING, True)
    glfw.window_hint(glfw.SAMPLES, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    window = glfw.create_window(width, height, 'bright', None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError('Could not create GLFW window.')

    # Make the window's context current
    glfw.make_context_current(window)

    # Set global OpenGL parameters.
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_TRUE)

    return window


_window = _create_window(1, 1)
