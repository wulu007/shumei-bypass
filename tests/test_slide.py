import cv2
import numpy as np
import pytest

from wulu_shumei_bypass.shumei import Shumei
from wulu_shumei_bypass.slover.slide import solve_slide


def paste_foreground(
    bg: cv2.typing.MatLike, fg: cv2.typing.MatLike, x: int, y: int = 0
) -> cv2.typing.MatLike:
    bg = bg.copy()
    fg_h, fg_w = fg.shape[:2]
    if x + fg_w > bg.shape[1]:
        x = bg.shape[1] - fg_w
    if fg.shape[2] == 4:
        alpha = fg[:, :, 3] / 255.0
        for c in range(3):
            bg[y : y + fg_h, x : x + fg_w, c] = (1 - alpha) * bg[
                y : y + fg_h, x : x + fg_w, c
            ] + alpha * fg[:, :, c]
    else:
        bg[y : y + fg_h, x : x + fg_w] = fg[:, :, :3]
    return bg


@pytest.mark.asyncio
async def test_slide_predict(resource_dir, test_org):
    s = Shumei(organization=test_org, mode='slide')
    reg = await s.register()
    bg = await s.fetch_img(reg['bg'])
    fg = await s.fetch_img(reg['fg'])

    x_ratio = solve_slide(bg, fg)
    img = cv2.imdecode(np.frombuffer(bg, np.uint8), cv2.IMREAD_COLOR)
    fg_img = cv2.imdecode(np.frombuffer(fg, np.uint8), cv2.IMREAD_UNCHANGED)
    assert img is not None, 'Failed to decode the background image'
    assert fg_img is not None, 'Failed to decode the foreground image'
    h, w = img.shape[:2]
    x_px = int(x_ratio * w)

    result = paste_foreground(img, fg_img, x_px)
    cv2.line(result, (x_px, 0), (x_px, h), (0, 0, 255), 2)
    cv2.line(
        result, (x_px + fg_img.shape[1], 0), (x_px + fg_img.shape[1], h), (0, 0, 255), 2
    )

    out = resource_dir / 'result_slide.jpg'
    cv2.imwrite(out, result)
    print(f'saved {out}')
    print(f'slide x_ratio={x_ratio:.4f}, x_px={x_px}/{w}')
