from unittest import TestCase

import numpy as np

import bright.mesh


class TestMesh(TestCase):
    """Test the bright.mesh.Mesh class"""

    def test_init(self):
        """Test the __init__ method and properties"""

        vertices = np.array([
            [0.0,  0.5, 0.0],
            [-0.5, -0.5, 0.0],
            [0.5, -0.5, 0.0],
        ])

        faces = np.array([
            [0, 1, 2],
        ])

        mesh = bright.mesh.Mesh(vertices, faces)
        np.testing.assert_array_almost_equal(mesh.colors, np.ones((3, 4)))
