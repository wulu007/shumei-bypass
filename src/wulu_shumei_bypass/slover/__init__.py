import importlib
from typing import TYPE_CHECKING

__all__ = [
    'solve_slide',
    'solve_spatial_select',
    'solve_icon',
    'solve_seq_select',
    'solve_select',
]

_PRIVATE_SOLVERS = {'solve_icon', 'solve_seq_select', 'solve_select'}


def _private_error(name: str) -> ImportError:
    return ImportError(
        f"'{name}' is a private extension module and is NOT "
        f'bundled with the open-source package. '
        f'Contact the author (wulu007) for licensing and '
        f'installation instructions.'
    )


if TYPE_CHECKING:
    from .icon import solve_icon
    from .select import solve_select
    from .seq_select import solve_seq_select
    from .slide import solve_slide
    from .spatial_select import solve_spatial_select


def __getattr__(name):
    if name in __all__:
        module_name = name.replace('solve_', '', 1)
        try:
            module = importlib.import_module(f'.{module_name}', package=__name__)
            return getattr(module, name)
        except ImportError as e:
            err = e

            def _missing_dependency_stub(*args, **kwargs):
                if name in _PRIVATE_SOLVERS:
                    raise _private_error(name) from err
                raise ImportError(
                    f"'{name}' requires optional dependencies. "
                    f'Install the corresponding extra. '
                    f'Underlying error: {err}'
                ) from err

            return _missing_dependency_stub

    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


def __dir__():
    return __all__
