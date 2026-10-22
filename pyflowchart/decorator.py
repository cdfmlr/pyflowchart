import functools
import inspect
import os
from typing import Any, Callable, Optional, Union

from pyflowchart.flowchart import Flowchart
from pyflowchart.output_html import output_html


def _normalize_output_kind(output: Optional[Union[str, os.PathLike[str], bool]], default_kind: str) -> str:
    if output is True:
        return "html"
    if output is False:
        return "none"
    if isinstance(output, str):
        lowered = output.lower()
        if lowered in {"html", "htm", "flowchart.html", "flowchart.htm"}:
            return "html"
        if lowered in {"dsl", "raw", "txt", "flowchart", "flowchart.dsl"}:
            return "dsl"
        return "html" if os.path.splitext(output)[1].lower() in {".html", ".htm"} else "dsl"
    if output is None:
        return default_kind
    return default_kind


def _resolve_target_path(output: Optional[Union[str, os.PathLike[str], bool]], func: Callable[..., Any], kind: str) -> str:
    if output is False:
        return ""
    if output is None:
        filename = f"{func.__name__}.{ 'html' if kind == 'html' else 'dsl' }"
        return filename
    if isinstance(output, (str, os.PathLike)):
        target = os.fspath(output)
        if os.path.splitext(target)[1]:
            return target
        return f"{target}.{'html' if kind == 'html' else 'dsl'}"
    return f"{func.__name__}.{'html' if kind == 'html' else 'dsl'}"


def flowchart(
    output: Optional[Union[str, os.PathLike[str], bool]] = None,
    *,
    field: str = "",
    inner: bool = True,
    simplify: bool = True,
    conds_align: bool = False,
    output_format: Optional[str] = None,
    return_dsl: bool = False,
):
    """Decorator that renders a function's source as a flowchart.

    Supported output modes:
      - HTML output: ``@flowchart('diagram.html')`` or ``@flowchart(output='html')``
      - Raw DSL output: ``@flowchart('diagram.dsl')`` or ``@flowchart(output='dsl')``

    When ``return_dsl=True`` the wrapper returns the generated flowchart DSL string
    instead of the original function result. This is useful when the caller wants to
    inspect or embed the raw DSL manually.

    The original function is still executed normally unless ``return_dsl`` is enabled.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            source = inspect.getsource(func)
            flow = Flowchart.from_code(
                source,
                field=field,
                inner=inner,
                simplify=simplify,
                conds_align=conds_align,
            )
            dsl = flow.flowchart()

            kind = _normalize_output_kind(output if output_format is None else output_format, "html")
            if output_format is not None:
                kind = output_format.lower()
                if kind not in {"html", "dsl"}:
                    raise ValueError("output_format must be one of {'html', 'dsl'}")

            target = _resolve_target_path(output, func, kind)
            if target:
                if kind == "html":
                    output_html(output_name=target, field_name=field or func.__name__, flowchart=dsl)
                else:
                    with open(target, "w", encoding="utf-8") as handle:
                        handle.write(dsl)

            if return_dsl:
                return dsl
            return result

        return wrapper

    return decorator


flowchart_html = flowchart
