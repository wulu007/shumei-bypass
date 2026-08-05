# wulu-shumei-bypass

<p align="center">
<a href="https://pypi.org/project/wulu-shumei-bypass/"><img alt="PyPI" src="https://img.shields.io/pypi/v/wulu-shumei-bypass.svg"></a>
<a href="https://pypi.org/project/wulu-shumei-bypass/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/wulu-shumei-bypass"></a>
<a href="https://github.com/wulu007/shumei-bypass/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/wulu007/shumei-bypass"></a>
<a href="https://github.com/wulu007/shumei-bypass"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/wulu007/shumei-bypass"></a>
</p>

<p align="center">
| <a href="./README.md"><b>English</b></a> | <b>简体中文</b> |
</p>

一个用于交互 Shumei（数美）验证码服务的 Python 框架——处理注册、图片拉取、参数加密和验证提交。

框架本身完全开源。特定验证码模式的逆向解析器以**私有扩展模块**的形式分发（见 [私有扩展](#私有扩展)）。

## 功能特性

- 🧩 **协议级集成** — 处理验证码注册、图片拉取、字段加密及提交
- 🔐 **加密开箱即用** — 按协议版本自动生成正确的加密参数名与 DES 加密字段（`selectData`、`mouseData`、`duration` 等）
- 🖱️ **拟真轨迹生成** — 为滑块验证码生成类人的鼠标移动轨迹
- 🧠 **可插拔解析器架构** — 通过 `@Shumei.add_solver` 为每个模式注册自定义解析器，或使用私有扩展
- 📦 **多模式支持** — `slide`、`auto_slide`、`select`、`icon_select`、`seq_select`、`spatial_select`

## 安装

```bash
uv add wulu-shumei-bypass
# 或
pip install wulu-shumei-bypass
```

### 可选依赖

| 模式 | 状态 | 可选依赖 |
|---|---|---|
| `slide` | ✅ | `wulu-shumei-bypass[cv]` |
| `spatial_select` | ✅ | `wulu-shumei-bypass[cv]` |
| `auto_slide` | ✅ | — |
| `icon_select` | 🔒 | — |
| `seq_select` | 🔒 | — |
| `select` | ❌ | — |

图例：✅ = 开源可用 · 🔒 = 需要私有扩展 · ❌ = 暂不支持

## 快速开始

### 注册并验证（滑块）

```python
import asyncio

from wulu_shumei_bypass import Shumei


async def main():
    s = Shumei(
        organization='你的-organization-id',
        mode='slide',
    )
    result = await s.solve()
    print(result)


asyncio.run(main())
```

### 手动注册并拉取图片

```python
import asyncio

from wulu_shumei_bypass import Shumei


async def main():
    s = Shumei(organization='你的-organization-id', mode='icon_select')
    reg = await s.register()          # -> RegisterResult (rid, bg, fg, ...)
    bg = await s.fetch_img(reg['bg'])  # 背景图原始字节
    fg = await s.fetch_img(reg['fg'])  # 前景图原始字节


asyncio.run(main())
```

### 自定义解析器 + 底层验证

```python
import asyncio

from wulu_shumei_bypass import Shumei


@Shumei.add_solver('seq_select')
def solve_seq(bg: bytes) -> list[list[float]]:
    # 返回按点击顺序排列的 [x比例, y比例] 坐标列表
    ...


async def main():
    s = Shumei(organization='你的-organization-id', mode='seq_select')
    reg = await s.register()
    result = await s.fverify(reg)
    print(result)  # {'code': 1100, 'riskLevel': 'PASS', ...}


asyncio.run(main())
```

## API 概览

### `Shumei(**params)`

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `organization` | `str` | *(必填)* | 数美分配的机构 ID |
| `app_id` | `str` | `default` | 应用 ID |
| `channel` | `str` | `default` | 渠道标识 |
| `version` | `str` | `1.0.4` | 协议版本（`rversion`） |
| `sdkver` | `str` | `1.1.3` | SDK 版本 |
| `mode` | `Mode` | `slide` | 验证码模式 |
| `lang` | `str` | `zh-cn` | 语言 |
| `os_type` | `OSType` | `web_pc` | 系统类型（`web_pc` / `web_mobile`） |
| `captcha_uuid` | `str` | 自动生成 | 会话 UUID |
| `xhr_hooked` | `bool` | `True` | 目标站点是否 hook 了 XHR |
| `custom_data` | `dict` | `{}` | 注册时附加的额外数据 |

### 方法

- `await s.register() -> RegisterResult` — 获取新的验证码挑战
- `await s.fetch_img(path: str) -> bytes` — 下载验证码图片
- `await s.fverify(reg: RegisterResult) -> VerifyResult` — 提交解析结果
- `await s.solve(retry: int = 3) -> VerifyResult` — 注册 → 解析 → 验证，直到 PASS
- `@Shumei.add_solver(mode)` — 为某模式注册自定义解析器

### 解析器契约

每个解析器接收图片字节，返回**点击坐标比例**（相对图片尺寸 0.0–1.0），**按点击顺序**排列：

| 模式 | 签名 |
|---|---|
| `slide` | `(bg: bytes, fg: bytes) -> float`（滑动比例） |
| `auto_slide` | *(无需解析器)* |
| `spatial_select` | `(bg: bytes, order: str) -> tuple[float, float]` |
| `icon_select` | `(bg: bytes, fg: bytes) -> list[list[float]]` |
| `select` | `(bg: bytes, order: list[str]) -> list[list[float]]` |
| `seq_select` | `(bg: bytes) -> list[list[float]]` |

## 私有扩展

`icon_select`、`seq_select`、`select` 的解析器**不随本开源包分发**。它们存放在私有仓库中，安装后自动加载：

- `wulu-shumei-bypass-icon`
- `wulu-shumei-bypass-seq`

如需获取私有扩展，请联系作者。

## 开发

```bash
uv sync --dev
uv run pytest
```

## 免责声明

> ⚠️ **仅供学习与研究使用。** 使用风险自负。

本项目仅用于安全研究、逆向工程教学和互操作性测试。作者不对任何滥用、未授权访问或违反第三方服务条款的行为负责。请确保你的使用符合适用法律及你所交互服务的条款。

## License

[MIT](LICENSE)
