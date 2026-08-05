import cv2
import numpy as np


def solve_slide(bg_bytes: bytes, slice_bytes: bytes, scale=0.5) -> float:
    bg = cv2.imdecode(np.frombuffer(bg_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    sl = cv2.imdecode(np.frombuffer(slice_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
    if bg is None or sl is None:
        raise ValueError('Failed to decode images. Please check the input bytes.')
    if scale < 1:
        bg = cv2.resize(bg, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        sl = cv2.resize(sl, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    sl_gray = cv2.cvtColor(sl[:, :, :3], cv2.COLOR_BGR2GRAY)
    mask = sl[:, :, 3]
    res = cv2.matchTemplate(bg, sl_gray, cv2.TM_CCOEFF_NORMED, mask=mask)
    max_loc = cv2.minMaxLoc(res)[-1]
    return max_loc[0] / bg.shape[1]
