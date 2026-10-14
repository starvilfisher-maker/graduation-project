"""Small, dependency-free utilities; no training pipeline is implemented yet."""

from .metrics import BinarySegmentationMetrics, binary_segmentation_metrics

__all__ = ["BinarySegmentationMetrics", "binary_segmentation_metrics"]

