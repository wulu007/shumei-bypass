"""开发环境一键设置脚本。

用途：
  开发前运行一次，自动拉取私有扩展子模块并安装为可编辑依赖。

用法：
  uv run scripts/dev_setup.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIVATE_PACKAGES = [
    'extensions/shumei-bypass-icon',
    'extensions/shumei-bypass-seq',
]


def run(cmd: str, cwd: Path | None = None) -> None:
    print(f'>>> {cmd}')
    subprocess.run(cmd, shell=True, check=True, cwd=cwd or ROOT)


def main() -> int:
    print('== 1/3 拉取私有扩展子模块 ==')
    run('git submodule update --init --recursive')

    print('== 2/3 同步项目依赖 ==')
    run('uv sync --dev')

    print('== 3/3 安装私有扩展（可编辑）==')
    for pkg in PRIVATE_PACKAGES:
        if (ROOT / pkg / 'pyproject.toml').exists():
            run(f'uv pip install -e {pkg}')

    print('完成。私有扩展已安装，entry points 已注册。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
