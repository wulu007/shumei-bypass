import random


def generate(distance: int, y_base: int = 0, duration: int = 0) -> list[list[int]]:
    duration = duration or random.randint(500, 1200)
    n = duration // 100 + 1
    points = [[0, y_base, 0]]
    y = y_base
    for i in range(1, n):
        eased = (i / (n - 1)) ** 0.5
        x = round(eased * distance)
        y += random.randint(-1, 1)
        t = i * 100 + random.randint(2, 8)
        points.append([x, round(y), t])
    points[-1] = [distance, points[-1][1], (n - 1) * 100 + random.randint(0, 5)]
    return points


def times(start: int, end: int, n: int) -> list[int]:
    """生成 n 个递增的绝对时间戳，范围 [start, end] 内，最后一个贴近 end"""
    if n <= 1:
        return [start]
    if end <= start:
        return [start] * n
    span = end - start
    offsets = sorted(random.random() for _ in range(n))
    offsets[-1] = 1.0  # 保证最后一个点 = end
    return [start + round(span * o) for o in offsets]
