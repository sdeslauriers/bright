from abc import abstractmethod
from typing import Iterable
from typing import Union

import numpy as np
import pyrr
from OpenGL.GL import *
from OpenGL.GL import shaders


class Camera(object):

    def __init__(self,
                 location: Union[np.ndarray, Iterable],
                 target: Union[np.ndarray, Iterable],
                 width: int = 256,
                 height: int = 256):
        """Represents a camera that takes snapshots of a scene

        The Camera class represents a camera that takes pictures of a scene. It
        camera dictates how the scene is rendered.

        Args:
             location: The position of the camera in 3D space. Can be any
                object that can be converted to a numpy array with a
                shape of (3,).
            target: The target of the camera in 3D space. Can be any object
                that can be converted to a numpy array of floats with a shape
                of (3,).
            width: The width of the camera output in pixels. Must be a strictly
                positive integer.
            height: The height of the camera output in pixels. Must be a
                strictly positive integer.
        """

        self._location = None
        self._target = None

        try:
            height = max(1, height)
            height = np.uint32(height)
        except (TypeError, ValueError):
            raise TypeError('The height of the camera must be a strictly '
                            'positive integer.')
        self._height = height

        try:
            width = max(1, width)
            width = np.uint32(width)
        except (TypeError, ValueError):
            raise TypeError('The width of the camera must be an integer.')
        self._width = width

        self.location = location
        self.target = target

        self.up = [0, 1, 0]
        self.fov = 45.0
        self.clip = (1, 1e9)

    @property
    def height(self) -> int:
        """Returns the height of the camera output in pixels"""
        return self._height

    @property
    def location(self) -> int:
        """Returns the location of the camera"""
        return self._location

    @location.setter
    def location(self, location: Union[np.ndarray, Iterable, int, float]):
        """Sets the location of the camera

        Args:
             location: The position of the camera in 3D space. Can be any
                object that can be converted to a numpy array with a
                shape of (3,).

        """

        try:
            location = np.array(location, dtype='f4')
        except (TypeError, ValueError):
            raise TypeError('The location of the camera must be convertible '
                            'to a numpy array of float.')
        self._location = location

    @property
    def target(self) -> np.ndarray:
        """Returns the target of the camera"""
        return self._target

    @target.setter
    def target(self, target: Union[np.ndarray, Iterable, int, float]):
        """Sets the target (look at) of the camera

        Args:
            target: The target of the camera in 3D space. Can be any object
                that can be converted to a numpy array of floats with a shape
                of (3,).

        """

        try:
            target = np.array(target, dtype='f4')
        except (TypeError, ValueError):
            raise TypeError('The target of the camera must be convertible '
                            'to a numpy array of float.')
        self._target = target

    @property
    def view(self) -> np.ndarray:
        """Returns the view matrix of the camera"""
        return pyrr.matrix44.create_look_at(
            self.location, self.target, self.up)

    @property
    def width(self) -> int:
        """Returns the width of the camera output"""
        return self._width


class Frame(object):

    def __init__(self,
                 width: int,
                 height: int,
                 background: Union[np.ndarray, Iterable]):
        """A frame where a renderer can render an image

        Args:
            width: The width of the camera output in pixels. Must be a strictly
                positive integer.
            height: The height of the camera output in pixels. Must be a
                strictly positive integer.
            background: The color of the background. Can be any object that
                can be converted to a numpy array of float with a shape
                of (4,).
        """

        try:
            height = max(1, height)
            height = np.uint32(height)
        except (TypeError, ValueError):
            raise TypeError('The height of the camera must be a strictly '
                            'positive integer.')
        self._height = height

        try:
            width = max(1, width)
            width = np.uint32(width)
        except (TypeError, ValueError):
            raise TypeError('The width of the camera must be an integer.')
        self._width = width

        self._background = background

        self._handle = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.handle)

        # Color attachment.
        self._color = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._color)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                               GL_TEXTURE_2D, self._color, 0)

        # Depth attachment.
        self._depth = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._depth)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, width, height,
                     0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                               GL_TEXTURE_2D, self._depth, 0)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    @property
    def color(self) -> np.ndarray:
        """Returns the color of the frame"""

        glBindTexture(GL_TEXTURE_2D, self._color)
        raw_data = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGB, GL_UNSIGNED_BYTE)
        image_data = np.frombuffer(raw_data, dtype=np.uint8)
        color = image_data.reshape((self.height, self.width, 3))[::-1]

        return color

    @property
    def handle(self):
        """Returns the handle of the frame"""
        return self._handle

    @property
    def height(self) -> int:
        """Returns the height of the frame in pixels"""
        return self._height

    @property
    def width(self) -> int:
        """Returns the width of the frame in pixels"""
        return self._height

    def clear(self):
        """Clears the frame to its background color"""
        self.bind()
        glClearColor(*self._background)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def bind(self):
        """Bind the frame to render to it"""
        glBindFramebuffer(GL_FRAMEBUFFER, self.handle)


class Renderable(object):
    """Base class for renderable geometry

    The Renderable class defines the interface that all renderable geometry
    classes must implement.

    """

    pass


class Renderer(object):
    def __init__(self,
                 camera: Camera,
                 background: Union[np.ndarray, Iterable]=(1, 1, 1, 0)):
        """Base class for renderers

        The Renderer class defines the interface that all renderering classes
        must implement.

        Args:
            camera: The camera used to render the image.
            background: The background color of the image.

        """

        self._camera = camera
        self._frame = Frame(camera.width, camera.height, background)

    @property
    def camera(self):
        """Returns the camera used to render"""
        return self._camera

    @property
    def frame(self):
        """Returns the output frame of the renderer"""
        return self._frame

    @abstractmethod
    def render(self):
        """Renders the meshes into the frame"""
        pass


class Shader(object):
    def __init__(self, vertex_code, fragment_code):
        """Base class for shaders

        The Shader class defines the interface that all shaders must implement.

        Args:
            vertex_code: The GLSL vertex shader code.
            fragment_code: The GLSL fragment shader code.

        """

        # Compile the vertex and shader code.
        vertex_shader = shaders.compileShader(
            vertex_code, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(
            fragment_code, GL_FRAGMENT_SHADER)

        # Compile the program.
        self._program = shaders.compileProgram(vertex_shader, fragment_shader)

    def use(self):
        """Use the shader to render the geometry"""
        shaders.glUseProgram(self._program)
