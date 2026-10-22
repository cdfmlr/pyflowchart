import functools
import inspect
import os
from typing import Any, Callable, Optional, Union

from pyflowchart.flowchart import Flowchart
from pyflowchart.output_html import output_html


def _resolve_output_name(output_name: Optional[Union[str, os.PathLike[str]]], func: Callable[..., Any]) -> str:
    """Resolve the target HTML output name for a decorated function."""
    if output_name is None:
        target = f"{func.__name__}.html"
    else:
        target = os.fspath(output_name)

    if not os.path.splitext(target)[1].lower() in {".html", ".htm"}:
        target = f"{target}.html"
    return target


def flowchart(
    output_name: Optional[Union[str, os.PathLike[str]]] = None,
    *,
    field: str = "",
    inner: bool = True,
    simplify: bool = True,
    conds_align: bool = False,
):
    """Decorator that generates an HTML flowchart for a function.

    The original function is still called normally. After execution, the function's
    source is parsed into a flowchart and written to an HTML file using the
    project's built-in HTML renderer.

    Example:
        @flowchart("demo.html")
        def foo():
            ...
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
            target_name = _resolve_output_name(output_name, func)
            output_html(
                output_name=target_name,
                field_name=field or func.__name__,
                flowchart=flow.flowchart(),
            )
            return result

        return wrapper

    return decorator


flowchart_html = flowchart
