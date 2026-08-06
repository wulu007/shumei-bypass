import importlib
from typing import TYPE_CHECKING, Callable

__all__ = [
    'solve_slide',
    'solve_spatial_select',
    'solve_icon',
    'solve_seq_select',
    'solve_select',
]

# 通过 entry points 分发的私有 solver（由私有扩展包注册）
_PRIVATE_SOLVERS = {'solve_icon', 'solve_seq_select'}
_PRIVATE_EP_GROUP = 'wulu_shumei_bypass.solvers'


def _private_error(name: str) -> ImportError:
    return ImportError(
        f"'{name}' is a private extension module and is NOT "
        f'bundled with the open-source package. '
        f'Contact the author (wulu007) for licensing and '
        f'installation instructions.'
    )


def _discover_private() -> dict[str, Callable]:
    """从 entry points 发现私有 solver，返回 {mode: solver}"""
    try:
        from importlib.metadata import entry_points

        eps = entry_points(group=_PRIVATE_EP_GROUP)
    except Exception:
        return {}
    return {ep.name: ep.load() for ep in eps}


if TYPE_CHECKING:
    from .icon import solve_icon
    from .select import solve_select
    from .seq_select import solve_seq_select
    from .slide import solve_slide
    from .spatial_select import solve_spatial_select


def __getattr__(name):
    if name in __all__:
        module_name = name.replace('solve_', '', 1)

        if name in _PRIVATE_SOLVERS:
            private = _discover_private()
            if name in private:
                return private[name]
            return lambda *a, **k: (_ for _ in ()).throw(_private_error(name))

        try:
            module = importlib.import_module(f'.{module_name}', package=__name__)
            return getattr(module, name)
        except ImportError as e:
            err = e

            def _missing_dependency_stub(*args, **kwargs):
                raise ImportError(
                    f"'{name}' requires optional dependencies. "
                    f'Install the corresponding extra. '
                    f'Underlying error: {err}'
                ) from err

            return _missing_dependency_stub

    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def __dir__():
    return __all__
