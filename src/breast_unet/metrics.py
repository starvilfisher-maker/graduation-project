"""Case-level binary segmentation scores with explicit empty-mask handling.

Call once per case on already thresholded, flattened binary masks. Normal
images must be reported separately from lesion-positive cases. An empty target
and empty prediction produce undefined overlap scores (None), never a perfect
lesion-segmentation score. No smoothing constant modifies exact empty cases.
"""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class BinarySegmentationMetrics:
    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int
    dice: float | None
    iou: float | None
    target_present: bool
    predicted_positive_pixels: int
    predicted_positive_fraction: float


def _binary_values(values: Iterable[int], name: str) -> tuple[int, ...]:
    try:
        result = tuple(values)
    except TypeError as exc:
        raise ValueError(f"{name} must be an iterable of binary values") from exc
    if not result:
        raise ValueError(f"{name} must not be empty")
    if any(value not in (0, 1) for value in result):
        raise ValueError(f"{name} must contain only 0 and 1")
    return tuple(int(value) for value in result)


def binary_segmentation_metrics(
    target: Iterable[int], prediction: Iterable[int]
) -> BinarySegmentationMetrics:
    """Compute binary Dice/IoU and counts, treating every input as one case.

    Inputs must contain the same nonzero number of binary values. Probabilities
    are deliberately rejected: a threshold must be selected using validation
    data before this function is called on test predictions.
    """
    target_values = _binary_values(target, "target")
    predicted_values = _binary_values(prediction, "prediction")
    if len(target_values) != len(predicted_values):
        raise ValueError("target and prediction must have the same length")

    tp = fp = fn = tn = 0
    for actual, predicted in zip(target_values, predicted_values):
        if actual == 1:
            if predicted == 1:
                tp += 1
            else:
                fn += 1
        elif predicted == 1:
            fp += 1
        else:
            tn += 1

    union = tp + fp + fn
    dice_denominator = 2 * tp + fp + fn
    return BinarySegmentationMetrics(
        true_positive=tp,
        false_positive=fp,
        false_negative=fn,
        true_negative=tn,
        dice=2 * tp / dice_denominator if dice_denominator else None,
        iou=tp / union if union else None,
        target_present=bool(tp + fn),
        predicted_positive_pixels=tp + fp,
        predicted_positive_fraction=(tp + fp) / len(target_values),
    )

