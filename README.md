# wulu-shumei-bypass

<p align="center">
<a href="https://pypi.org/project/wulu-shumei-bypass/"><img alt="PyPI" src="https://img.shields.io/pypi/v/wulu-shumei-bypass.svg"></a>
<a href="https://pypi.org/project/wulu-shumei-bypass/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/wulu-shumei-bypass"></a>
<a href="https://github.com/wulu007/shumei-bypass/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/wulu007/shumei-bypass"></a>
<a href="https://github.com/wulu007/shumei-bypass"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/wulu007/shumei-bypass"></a>
</p>

<p align="center">
| <b>English</b> | <a href="./README.zh-CN.md"><b>简体中文</b></a> |
</p>

A Python framework for interacting with Shumei (数美) CAPTCHA service — handles registration, image fetching, parameter encryption, and verification submission.

The framework itself is fully open-source. Reverse-engineered solvers for specific captcha modes are distributed as **private extension modules** (see [Private Extensions](#private-extensions)).

## Features

- 🧩 **Protocol-level integration** — handles captcha registration, image fetching, field encryption, and verification submission against the Shumei (数美) API
- 🔐 **Correct encryption out of the box** — DES-encrypted protocol fields (`selectData`, `mouseData`, `duration`, etc.) with the right parameter names per protocol version
- 🖱️ **Realistic trajectory generation** — human-like mouse movement paths for slide captchas
- 🧠 **Pluggable solver architecture** — register your own solver per mode with `@Shumei.add_solver`, or use the private extensions
- 📦 **Multi-mode support** — `slide`, `auto_slide`, `select`, `icon_select`, `seq_select`, `spatial_select`

## Installation

```bash
uv add wulu-shumei-bypass
# or
pip install wulu-shumei-bypass
```

### Optional extras

| Mode | Status | Extra |
|---|---|---|
| `slide` | ✅ | `wulu-shumei-bypass[cv]` |
| `spatial_select` | ✅ | `wulu-shumei-bypass[cv]` |
| `auto_slide` | ✅ | — |
| `icon_select` | 🔒 | — |
| `seq_select` | 🔒 | — |
| `select` | ❌ | — |

Legend: ✅ = open source · 🔒 = private extension · ❌ = not available

## Quick Start

### Register & verify (slide)

```python
import asyncio

from wulu_shumei_bypass import Shumei


async def main():
    s = Shumei(
        organization='your-organization-id',
        mode='slide',
    )
    result = await s.solve()
    print(result)


asyncio.run(main())
```

### Register manually & fetch images

```python
import asyncio

from wulu_shumei_bypass import Shumei


async def main():
    s = Shumei(organization='your-organization-id', mode='icon_select')
    reg = await s.register()          # -> RegisterResult (rid, bg, fg, ...)
    bg = await s.fetch_img(reg['bg'])  # raw bytes of background image
    fg = await s.fetch_img(reg['fg'])  # raw bytes of foreground image


asyncio.run(main())
```

### Low-level verify with a custom solver

```python
import asyncio

from wulu_shumei_bypass import Shumei


@Shumei.add_solver('seq_select')
def solve_seq(bg: bytes) -> list[list[float]]:
    # return a list of [x_ratio, y_ratio] click points in click order
    ...


async def main():
    s = Shumei(organization='your-organization-id', mode='seq_select')
    reg = await s.register()
    result = await s.fverify(reg)
    print(result)  # {'code': 1100, 'riskLevel': 'PASS', ...}


asyncio.run(main())
```

## API Overview

### `Shumei(**params)`

| Param | Type | Default | Description |
|---|---|---|---|
| `organization` | `str` | *(required)* | Organization ID assigned by Shumei |
| `app_id` | `str` | `default` | Application ID |
| `channel` | `str` | `default` | Channel identifier |
| `version` | `str` | `1.0.4` | Protocol version (`rversion`) |
| `sdkver` | `str` | `1.1.3` | SDK version |
| `mode` | `Mode` | `slide` | Captcha mode |
| `lang` | `str` | `zh-cn` | Language |
| `os_type` | `OSType` | `web_pc` | OS type (`web_pc` / `web_mobile`) |
| `captcha_uuid` | `str` | auto | Session UUID (auto-generated) |
| `xhr_hooked` | `bool` | `True` | Whether the target site hooks XHR |
| `custom_data` | `dict` | `{}` | Extra data sent with registration |

### Methods

- `await s.register() -> RegisterResult` — obtain a new captcha challenge
- `await s.fetch_img(path: str) -> bytes` — download a captcha image
- `await s.fverify(reg: RegisterResult) -> VerifyResult` — submit a solution
- `await s.solve(retry: int = 3) -> VerifyResult` — register → solve → verify until PASS
- `@Shumei.add_solver(mode)` — register a custom solver for a mode

### Solver contract

Each solver receives the image bytes and returns click coordinates **as ratios** (0.0–1.0 relative to image dimensions), in **click order**:

| Mode | Signature |
|---|---|
| `slide` | `(bg: bytes, fg: bytes) -> float` (slide ratio) |
| `auto_slide` | *(no solver needed)* |
| `spatial_select` | `(bg: bytes, order: str) -> tuple[float, float]` |
| `icon_select` | `(bg: bytes, fg: bytes) -> list[list[float]]` |
| `select` | `(bg: bytes, order: list[str]) -> list[list[float]]` |
| `seq_select` | `(bg: bytes) -> list[list[float]]` |

## Private Extensions

Solvers for `icon_select`, `seq_select`, and `select` are **not** bundled with this open-source package. They live in private repositories and are loaded automatically when installed:

- `wulu-shumei-bypass-icon`
- `wulu-shumei-bypass-seq`

Contact the author for access to the private extensions.

## Development

```bash
uv sync --dev
uv run pytest
```

## Disclaimer

> ⚠️ **For educational and research purposes only.** Use at your own risk.

This project is intended solely for security research, reverse-engineering education, and interoperability testing. The author is not responsible for any misuse, unauthorized access, or violation of third-party terms of service. Always ensure your use complies with applicable laws and the terms of the services you interact with.

## License

[MIT](LICENSE)
