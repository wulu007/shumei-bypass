import cv2
import numpy as np


def get_shadow_mask(img: cv2.typing.MatLike, threshold=20):
    r, g, b = cv2.split(img)
    avg = np.mean(img, axis=2, dtype=np.int16)
    dev_r = np.abs(np.int16(r) - avg)
    dev_g = np.abs(np.int16(g) - avg)
    dev_b = np.abs(np.int16(b) - avg)
    mask = (dev_r < threshold) & (dev_g < threshold) & (dev_b < threshold)
    result = np.full(img.shape[:2], 255, dtype=np.uint8)
    result[mask] = 0
    return result


def get_min_contour(img: cv2.typing.MatLike):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError('No contours found in the image.')
    min_contour = min(
        contours,
        key=lambda c: cv2.boundingRect(c)[2] * cv2.boundingRect(c)[3],
    )
    x, y, w, h = cv2.boundingRect(min_contour)
    return x + w // 2, y + h // 2


def solve_spatial_select(
    img_bytes: bytes, order: str = '', scale=0.5
) -> tuple[float, float]:
    img_array = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError('Failed to decode image. Please check the input bytes.')
    if scale != 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    img = get_shadow_mask(img)
    kernel = np.ones((3, 3), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=2)
    distance_transform = cv2.distanceTransform(img, cv2.DIST_L2, 3)
    _, binary = cv2.threshold(
        distance_transform, 0.1 * distance_transform.max(), 255, cv2.THRESH_BINARY
    )
    x, y = get_min_contour(np.uint8(binary))  # type: ignore
    return x / img.shape[1], y / img.shape[0]
