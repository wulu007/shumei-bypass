import os
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from wulu_shumei_bypass.shumei import Shumei
from wulu_shumei_bypass.slover.spatial_select import solve_spatial_select


def cv2_put_text(img, text, pos, color=(0, 0, 255), size=28, anchor='lt'):
    font_path = Path(os.environ.get('SystemRoot', 'C:\\Windows')) / 'Fonts' / 'msyh.ttc'
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    font = ImageFont.truetype(font_path, size)
    draw.text(pos, text, font=font, fill=color[::-1], anchor=anchor)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


@pytest.mark.asyncio
async def test_spatial_predict(resource_dir, test_org):
    s = Shumei(organization=test_org, mode='spatial_select')
    reg = await s.register()
    bg = await s.fetch_img(reg['bg'])

    x_ratio, y_ratio = solve_spatial_select(bg)
    img = cv2.imdecode(np.frombuffer(bg, np.uint8), cv2.IMREAD_COLOR)
    assert img is not None, 'Failed to decode the background image'

    h, w = img.shape[:2]
    x_px, y_px = int(x_ratio * w), int(y_ratio * h)

    order = (reg.get('order') or ['order'])[0]
    cv2.circle(img, (x_px, y_px), 8, (0, 0, 255), -1)
    cv2.circle(img, (x_px, y_px), 14, (0, 0, 255), 2)
    img = cv2_put_text(img, order, (w // 2, 20), size=20, anchor='mt')

    out = resource_dir / 'result_spatial.jpg'
    cv2.imwrite(out, img)
    print(f'saved {out}')
    print(f'spatial x_ratio={x_ratio:.4f}, y_ratio={y_ratio:.4f}, pos=({x_px},{y_px})')
