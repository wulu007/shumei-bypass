from wulu_shumei_bypass_icon import solve_icon as _solve_icon


def solve_icon(bg_img: bytes, fp_img: bytes) -> list[list[float]]:
    return _solve_icon(bg_img, fp_img)
