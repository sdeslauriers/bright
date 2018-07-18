import nimesh
import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *
import pyrr

import bright.core


MODEL_VERTEX_LOCATION = 0
MODEL_VERTEX_COLOR = 1

CAMERA_VIEW_MATRIX = 0
CAMERA_PERSPECTIVE_MATRIX = 1


class Mesh(nimesh.Mesh):

    def __init__(self, vertices, faces, colors=None):

        super().__init__(vertices, faces)

        # If there is no color, make all vertices white.
        if colors is None:
            colors = np.ones((self.nb_vertices, 4))
        self._colors = colors

        # Each mesh has it own vertex array object.
        self._vao = glGenVertexArrays(1)
        glBindVertexArray(self._vao)

        # 3 floats for the location and 4 floats for the color.
        stride = 12 + 16

        # Setup vertex source and format.
        vbo_data = self.vertices

        # Add the color.
        vbo_data = np.hstack((vbo_data, colors))
        color_offset = 12

        self._vertex_vbo = vbo.VBO(vbo_data.astype('f4'),
                                   target=GL_ARRAY_BUFFER)
        self._vertex_vbo.bind()
        self._indices_vbo = vbo.VBO(self._triangles.astype('uint32'),
                                    target=GL_ELEMENT_ARRAY_BUFFER)
        self._indices_vbo.bind()

        glEnableVertexAttribArray(MODEL_VERTEX_LOCATION)
        glVertexAttribPointer(MODEL_VERTEX_LOCATION, 3, GL_FLOAT,
                              False, stride, self._vertex_vbo)

        glEnableVertexAttribArray(MODEL_VERTEX_COLOR)
        glVertexAttribPointer(MODEL_VERTEX_COLOR, 4, GL_FLOAT,
                              False, stride, self._vertex_vbo + color_offset)

    @property
    def colors(self):
        """Returns the vertex colors of the mesh"""
        return self._colors

    def draw(self):
        """Draws the mesh"""
        glBindVertexArray(self._vao)
        glDrawElements(GL_TRIANGLES, self.nb_triangles * 3,
                       GL_UNSIGNED_INT, self._indices_vbo)


class Renderer(bright.core.Renderer):

    def __init__(self, camera, meshes, **args):

        super().__init__(camera, **args)

        self.meshes = meshes
        self._shader = None

        self._shader = bright.core.Shader("""
        #version 430

        layout(location = 0) uniform mat4 camera_view_matrix;
        layout(location = 1) uniform mat4 camera_perpective_matrix;

        layout(location = 0) in vec3 model_vertex_position;
        layout(location = 1) in vec4 model_vertex_color;

        out vec4 color;

        void main() {
            gl_Position = camera_perpective_matrix * camera_view_matrix *
                          vec4(model_vertex_position, 1.0);
            color = model_vertex_color;
        }
        """, """
        #version 430

        in vec4 color;

        out vec4 fragment_color;

        void main() {
            fragment_color = color;
        }
        """)

    def render(self):
        """Render the meshes into the frame"""

        self._shader.use()
        self.frame.clear()

        glViewport(0, 0, self.camera.width, self.camera.height)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

        perspective_matrix = pyrr.matrix44.create_perspective_projection(
            self.camera.fov, self.camera.width / self.camera.height,
            *self.camera.clip)
        view_matrix = self.camera.view

        glUniformMatrix4fv(CAMERA_PERSPECTIVE_MATRIX, 1, GL_FALSE,
                           perspective_matrix)
        glUniformMatrix4fv(CAMERA_VIEW_MATRIX, 1, GL_FALSE, view_matrix)

        for mesh in self.meshes:
            mesh.draw()

        glDisable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
