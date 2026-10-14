"""Known numerical cases, including normal-image and missed-lesion edge cases."""

import unittest

from breast_unet.metrics import binary_segmentation_metrics


class BinarySegmentationMetricsTests(unittest.TestCase):
    def test_perfect_lesion(self):
        result = binary_segmentation_metrics([1, 1, 0, 0], [1, 1, 0, 0])
        self.assertEqual((result.dice, result.iou), (1.0, 1.0))
        self.assertEqual((result.true_positive, result.true_negative), (2, 2))

    def test_known_partial_overlap(self):
        # Target area 3, predicted area 4, overlap 2: Dice 4/7; IoU 2/5.
        result = binary_segmentation_metrics(
            [1, 1, 1, 0, 0, 0], [1, 1, 0, 1, 1, 0]
        )
        self.assertAlmostEqual(result.dice, 4 / 7)
        self.assertAlmostEqual(result.iou, 2 / 5)
        self.assertEqual(result.false_positive, 2)
        self.assertEqual(result.false_negative, 1)

    def test_disjoint_lesions(self):
        result = binary_segmentation_metrics([1, 0], [0, 1])
        self.assertEqual((result.dice, result.iou), (0.0, 0.0))

    def test_completely_missed_lesion(self):
        result = binary_segmentation_metrics([1, 1, 0], [0, 0, 0])
        self.assertTrue(result.target_present)
        self.assertEqual((result.dice, result.iou), (0.0, 0.0))
        self.assertEqual(result.false_negative, 2)

    def test_normal_without_false_detection_is_not_lesion_score(self):
        result = binary_segmentation_metrics([0, 0, 0], [0, 0, 0])
        self.assertIsNone(result.dice)
        self.assertIsNone(result.iou)
        self.assertFalse(result.target_present)
        self.assertEqual(result.predicted_positive_fraction, 0.0)

    def test_normal_with_false_detection(self):
        result = binary_segmentation_metrics([0, 0, 0, 0], [0, 1, 0, 0])
        self.assertFalse(result.target_present)
        self.assertEqual((result.dice, result.iou), (0.0, 0.0))
        self.assertEqual(result.false_positive, 1)
        self.assertEqual(result.predicted_positive_fraction, 0.25)

    def test_rejects_mismatched_and_empty_inputs(self):
        for target, prediction in [([], []), ([0], []), ([0, 1], [0])]:
            with self.subTest(target=target, prediction=prediction):
                with self.assertRaises(ValueError):
                    binary_segmentation_metrics(target, prediction)

    def test_rejects_probabilities_and_nonbinary_values(self):
        for invalid in [0.1, 2, -1, float("nan"), "1", None]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    binary_segmentation_metrics([0, 1], [0, invalid])
                with self.assertRaises(ValueError):
                    binary_segmentation_metrics([0, invalid], [0, 1])


if __name__ == "__main__":
    unittest.main()

