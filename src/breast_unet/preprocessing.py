"""Deterministic BrEaST decoding. Image inference never takes a reference mask.

This policy is justified by the downloaded v1 encoding audit, not by model
performance. No cropping, augmentation, fitted normalization or file writes.
Optional numerical dependencies are imported inside functions.
"""

from pathlib import Path

POLICY = {
    "id": "breast_v1",
    "version": 1,
    "status": "implemented_data_qc_pending_full_experiment_freeze",
    "source_modes": ["L", "RGB", "RGBA"],
    "source_dtype": "uint8",
    "image_alpha": "composite_on_black_before_grayscale",
    "gray_weights_rgb": [0.299, 0.587, 0.114],
    "normalization": "divide_255_no_fitted_statistics",
    "image_resize": "Pillow_float32_bilinear",
    "mask_encoding": "equal_RGB_channels_values_0_255",
    "mask_foreground": "color_channel_equals_255",
    "mask_alpha": "positive_color_requires_positive_alpha_no_opacity_threshold",
    "mask_resize": "Pillow_uint8_nearest",
    "height": 256,
    "width": 256,
    "ground_truth_crop": False,
}


def _read_png(path: Path):
    import numpy as np
    from PIL import Image

    with Image.open(path) as image:
        if image.format != "PNG" or image.mode not in POLICY["source_modes"]:
            raise ValueError("unsupported_png_format_or_mode")
        image.load()
        array = np.asarray(image).copy()
        mode = image.mode
    if array.dtype != np.uint8:
        raise ValueError("expected_uint8")
    return array, mode


def read_visible_rgb(path: Path):
    """Float32 RGB in [0,1], respecting opacity and hiding alpha-zero RGB."""
    import numpy as np

    array, mode = _read_png(path)
    if mode == "L":
        rgb = np.repeat(array[..., None], 3, axis=2).astype(np.float32)
    else:
        rgb = array[..., :3].astype(np.float32)
    rgb /= np.float32(255)
    if mode == "RGBA":
        rgb *= array[..., 3:4].astype(np.float32) / np.float32(255)
    return rgb


def read_image(path: Path):
    """Native-size normalized grayscale. This function uses the image only."""
    import numpy as np

    rgb = read_visible_rgb(path)
    weights = np.asarray(POLICY["gray_weights_rgb"], dtype=np.float32)
    return np.clip(np.sum(rgb * weights, axis=2), 0, 1).astype(np.float32)


def read_mask(path: Path):
    """Decode a verified binary color label; alpha is not a soft target.

    Equal RGB channels and 0/255 labels are required. White with zero opacity
    is contradictory and rejected. Partially visible white stays foreground,
    including the two alpha=75 pixels observed in case010_tumor.png.
    """
    import numpy as np

    array, mode = _read_png(path)
    if mode == "L":
        label = array
    else:
        if not (np.array_equal(array[..., 0], array[..., 1])
                and np.array_equal(array[..., 0], array[..., 2])):
            raise ValueError("mask_color_channels_disagree")
        label = array[..., 0]
    if not np.all((label == 0) | (label == 255)):
        raise ValueError("mask_not_binary_0_255")
    if mode == "RGBA" and np.any((label == 255) & (array[..., 3] == 0)):
        raise ValueError("mask_hidden_positive_color")
    return (label == 255).astype(np.uint8)


def resize_image(gray):
    import numpy as np
    from PIL import Image

    gray = np.asarray(gray)
    if (gray.ndim != 2 or not gray.size or not np.isfinite(gray).all()
            or gray.min() < 0 or gray.max() > 1):
        raise ValueError("expected_finite_normalized_2d_image")
    image = Image.fromarray(gray.astype(np.float32))
    result = np.asarray(image.resize((256, 256), Image.Resampling.BILINEAR))
    return np.clip(result, 0, 1).astype(np.float32)


def resize_mask(mask):
    """Resize a binary label without introducing fractional labels.

    Empty inputs can represent verified normal cases. A disappearing positive
    target must be handled by prepare_target/audit, never relabeled normal.
    """
    import numpy as np
    from PIL import Image

    mask = np.asarray(mask)
    if mask.ndim != 2 or not mask.size or not np.all((mask == 0) | (mask == 1)):
        raise ValueError("expected_binary_2d_mask")
    return np.asarray(Image.fromarray(mask.astype(np.uint8)).resize(
        (256, 256), Image.Resampling.NEAREST)).astype(np.uint8)


def prepare_image(path: Path):
    """Return (256,256,1) float32 input with no dependence on annotations."""
    return resize_image(read_image(path))[..., None]


def prepare_target(path: Path):
    """Positive-cohort target; normal targets must be handled explicitly."""
    mask = read_mask(path)
    if not mask.any():
        raise ValueError("empty_positive_target")
    resized = resize_mask(mask)
    if not resized.any():
        raise ValueError("positive_target_disappears_at_256")
    return resized[..., None].astype("float32")
