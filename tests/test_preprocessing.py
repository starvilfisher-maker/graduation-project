"""Tests for target semantics, opacity, inference independence and resizing."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from breast_unet.preprocessing import POLICY

HAS_IMAGES = all(importlib.util.find_spec(name) is not None for name in ("numpy", "PIL"))
HAS_WORKBOOK = importlib.util.find_spec("openpyxl") is not None


class PolicyTests(unittest.TestCase):
    def test_recorded_policy_matches_executed_policy(self):
        path = Path(__file__).resolve().parents[1] / "configs/preprocessing_v1.json"
        self.assertEqual(json.loads(path.read_text()), POLICY)


@unittest.skipUnless(HAS_IMAGES, "optional numpy/Pillow dependencies unavailable")
class PreprocessingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "input.png"

    def tearDown(self):
        self.tmp.cleanup()

    def save(self, data):
        from PIL import Image
        Image.fromarray(data).save(self.path)

    def test_transparent_rgb_is_hidden_and_partial_alpha_composites_on_black(self):
        import numpy as np
        from breast_unet.preprocessing import read_visible_rgb
        self.save(np.array([[[255, 128, 90, 0], [255, 255, 255, 75]]], dtype=np.uint8))
        visible = read_visible_rgb(self.path)
        np.testing.assert_array_equal(visible[0, 0], [0, 0, 0])
        np.testing.assert_allclose(visible[0, 1], [75/255]*3, atol=1e-7)

    def test_grayscale_formula_on_primary_colors(self):
        import numpy as np
        from breast_unet.preprocessing import read_image
        self.save(np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255]]], dtype=np.uint8))
        np.testing.assert_allclose(read_image(self.path), [[0.299, 0.587, 0.114]], atol=1e-7)

    def test_mask_partial_opacity_keeps_reference_white_pixels(self):
        import numpy as np
        from breast_unet.preprocessing import read_mask
        self.save(np.array([[[0, 0, 0, 0], [255, 255, 255, 75], [255, 255, 255, 255]]], dtype=np.uint8))
        np.testing.assert_array_equal(read_mask(self.path), [[0, 1, 1]])

    def test_opaque_black_background_is_not_foreground(self):
        import numpy as np
        from breast_unet.preprocessing import read_mask
        self.save(np.array([[[0, 0, 0, 255], [255, 255, 255, 255]]], dtype=np.uint8))
        np.testing.assert_array_equal(read_mask(self.path), [[0, 1]])

    def test_contradictory_hidden_foreground_is_rejected(self):
        import numpy as np
        from breast_unet.preprocessing import read_mask
        self.save(np.array([[[255, 255, 255, 0]]], dtype=np.uint8))
        with self.assertRaisesRegex(ValueError, "hidden_positive"):
            read_mask(self.path)

    def test_colored_or_nonbinary_mask_rejected(self):
        import numpy as np
        from breast_unet.preprocessing import read_mask
        for pixel in ([255, 0, 0], [127, 127, 127]):
            with self.subTest(pixel=pixel):
                self.save(np.array([[pixel]], dtype=np.uint8))
                with self.assertRaises(ValueError):
                    read_mask(self.path)

    def test_unexpected_source_bit_depth_rejected(self):
        import numpy as np
        from breast_unet.preprocessing import read_image
        self.save(np.array([[0, 65535]], dtype=np.uint16))
        with self.assertRaises(ValueError):
            read_image(self.path)

    def test_image_tensor_deterministic_and_does_not_modify_input(self):
        import numpy as np
        from breast_unet.preprocessing import prepare_image
        self.save(np.arange(35, dtype=np.uint8).reshape(5, 7))
        original = self.path.read_bytes()
        first, second = prepare_image(self.path), prepare_image(self.path)
        self.assertEqual(first.shape, (256, 256, 1))
        self.assertEqual(first.dtype, np.float32)
        np.testing.assert_array_equal(first, second)
        self.assertTrue(np.isfinite(first).all())
        self.assertGreaterEqual(first.min(), 0)
        self.assertLessEqual(first.max(), 1)
        self.assertEqual(self.path.read_bytes(), original)

    def test_resizing_keeps_coordinate_alignment_and_binary_labels(self):
        import numpy as np
        from breast_unet.preprocessing import resize_image, resize_mask
        mask = np.zeros((2, 4), dtype=np.uint8)
        mask[:, :2] = 1
        resized = resize_mask(mask)
        self.assertEqual(set(np.unique(resized)), {0, 1})
        np.testing.assert_array_equal(resized[:, :128], 1)
        np.testing.assert_array_equal(resized[:, 128:], 0)
        image = resize_image(mask.astype(np.float32))
        self.assertGreater(image[:, 0].min(), 0.99)
        self.assertLess(image[:, -1].max(), 0.01)
        # Bilinear may be fractional; labels must never be interpolated this way.
        self.assertTrue(((image > 0) & (image < 1)).any())

    def test_invalid_arrays_rejected_before_resizing(self):
        import numpy as np
        from breast_unet.preprocessing import resize_image, resize_mask
        for invalid in (np.array([[float('nan')]]), np.array([[1.1]]), np.array([[-0.1]]), np.array([])):
            with self.subTest(array=invalid):
                with self.assertRaises(ValueError):
                    resize_image(invalid)
        with self.assertRaises(ValueError):
            resize_mask(np.array([[0.5]]))

    def test_empty_or_disappearing_positive_target_rejected(self):
        import numpy as np
        from breast_unet.preprocessing import prepare_target
        self.save(np.zeros((3, 3), dtype=np.uint8))
        with self.assertRaisesRegex(ValueError, "empty_positive"):
            prepare_target(self.path)
        small = np.zeros((512, 512), dtype=np.uint8)
        small[0, 0] = 255
        self.save(small)
        with self.assertRaisesRegex(ValueError, "disappears"):
            prepare_target(self.path)

    @unittest.skipUnless(HAS_WORKBOOK, "optional openpyxl unavailable")
    def test_policy_audit_handles_real_encoding_and_keeps_review_pending(self):
        import numpy as np
        from PIL import Image
        from openpyxl import Workbook
        from breast_unet.data_audit import IMAGE_DIRECTORY, WORKBOOK_FILENAME, audit_dataset
        root = Path(self.tmp.name)
        raw = root / "data/raw/example"
        images = raw / IMAGE_DIRECTORY
        images.mkdir(parents=True)
        workbook = Workbook()
        workbook.active.append(["CaseID", "Image_filename", "Mask_tumor_filename", "Mask_other_filename", "Classification", "Margin"])
        workbook.active.append([1, "case001.png", "case001_tumor.png", None, "benign", "circumscribed"])
        workbook.save(raw / WORKBOOK_FILENAME)
        image = np.full((8, 8, 4), 255, dtype=np.uint8)
        image[:, :, 1] = 120
        image[0, :, 3] = 0
        mask = np.zeros((8, 8, 4), dtype=np.uint8)
        mask[2:5, 2:5] = 255
        mask[2, 2, 3] = 75
        Image.fromarray(image).save(images / 'case001.png')
        Image.fromarray(mask).save(images / 'case001_tumor.png')
        result = audit_dataset(root, raw, root / 'data/audit/new', 'breast_v1')
        self.assertTrue(result['automatic_checks_passed'])
        self.assertEqual(result['mask_check_coverage']['masks_resize_checked'], 1)
        self.assertEqual(result['image_resize_checked'], 1)
        self.assertFalse(result['training_ready'])
        self.assertEqual(result['visual_review_status'], 'pending_visual_review')


if __name__ == '__main__':
    unittest.main()
