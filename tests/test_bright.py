from unittest import TestCase

import numpy as np

import bright


class TestRender(TestCase):
    """Test the bright.render function"""

    def test_render_square(self):
        """Test rendering a square"""

        # Create a renderer for a simple triangle.
        camera = bright.Camera((0, 0, 1 / np.tan(np.pi/8)), (0, 0, 0), 4, 4)
        mesh = bright.Mesh(
            [[0, 1, 0], [0, 0, 0], [1, 0, 0]],
            [[0, 1, 2]]
        )
        renderer = bright.MeshRenderer(camera, [mesh], background=(0, 0, 0, 0))

        # Render the frame.
        frames = bright.render([renderer])

        self.assertEqual(len(frames), 1)
        expected_frame = np.tile(np.array([
            [0, 0, 0, 0],
            [0, 0, 255, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ])[:, :, None], (1, 1, 3))
        np.testing.assert_array_almost_equal(expected_frame, frames[0])
