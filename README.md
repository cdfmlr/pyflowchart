# PyFlowchart

English | [机翻中文](README_zh-CN.md)

PyFlowchart is a Python package that lets you:

- Write flowcharts in Python.
- Translate Python source code into flowcharts.

PyFlowchart produces flowcharts in the [flowchart.js](https://github.com/adrai/flowchart.js) DSL, a widely used textual representation of flowcharts. You can convert these flowcharts to images using [flowchart.js.org](http://flowchart.js.org), [francoislaberge/diagrams](https://github.com/francoislaberge/diagrams/#flowchart), or some Markdown editors. You can also output the generated flowchart directly as an interactive HTML page.

## Get PyFlowchart

```sh
$ pip install pyflowchart
```

## Quick Start

Want to **flowchart your Python code in `example.py`?** Run this:

```sh
$ python -m pyflowchart example.py
# or, if pyflowchart is on your PATH:
$ pyflowchart example.py
```

> ⚠️ PyFlowchart requires **Python 3.7+** and is CI-tested on Python **3.7 through 3.14**. To check your Python version, run [`python --version`](https://docs.python.org/3/using/cmdline.html#cmdoption-version).
>
> If you have both Python 2 and Python 3 installed, you may need to use `python3` instead of `python`. This is becoming less common as [Python 2 is sunsetting](https://www.python.org/doc/sunset-python-2/).

PyFlowchart will print the generated flowchart.js DSL to stdout. You can paste the output into [flowchart.js.org](http://flowchart.js.org) or open it in editors like Typora to render the diagram.

**To output an HTML file** containing the rendered flowchart:

```sh
$ python -m pyflowchart example.py -o example.html
$ open example.html  # or open it manually in your browser
```

**To flowchart a specific function or method:**

```sh
$ python -m pyflowchart example.py -f function_name
# or a method inside a class:
$ python -m pyflowchart example.py -f ClassName.method_name
```

For example: `python -m pyflowchart example.py -f MyClass.add`.

🎉 **Now you are ready to flowchart your code!**

To learn more about how to use PyFlowchart, keep reading this document.

## Flowchart in Python

PyFlowchart lets you write flowcharts in Python, which can be automatically translated into the [flowchart.js](https://github.com/adrai/flowchart.js) DSL.

The following [flowchart.js node types](https://github.com/adrai/flowchart.js#node-types) are supported:

- StartNode
- OperationNode
- ConditionNode
- InputOutputNode
- SubroutineNode
- EndNode

To connect nodes, use the `connect()` method. For `ConditionNode`s, use `connect_yes()` or `connect_no()`. You can optionally pass a direction string as the second argument to any `connect` call.

Create a `Flowchart` with your start node and call its `flowchart()` method to get the flowchart.js DSL:

```python
from pyflowchart import *

st = StartNode('a_pyflow_test')
op = OperationNode('do something')
cond = ConditionNode('Yes or No?')
io = InputOutputNode(InputOutputNode.OUTPUT, 'something...')
sub = SubroutineNode('A Subroutine')
e = EndNode('a_pyflow_test')

st.connect(op)
op.connect(cond)
cond.connect_yes(io)
cond.connect_no(sub)
sub.connect(op, "right")  # sub->op line starts from the right of sub
io.connect(e)

fc = Flowchart(st)
print(fc.flowchart())
```

Output:

```
st0=>start: start a_pyflow_test
op1=>operation: do something
cond2=>condition: Yes or No?
io3=>inputoutput: output: something...
e5=>end: end a_pyflow_test
sub4=>subroutine: A Subroutine

st0->op1
op1->cond2
cond2->
cond2->
cond2(yes)->io3
io3->e5
cond2(no)->sub4
sub4(right)->op1
```

You can visit http://flowchart.js.org and paste the generated DSL to render an SVG flow diagram:

![screenshot on flowchart.js page](docs/imgs/flowchart-js-org.png)

You can also call `pyflowchart.output_html` to generate a standalone HTML page with the rendered flowchart:

```python
output_html('output.html', 'a_pyflow_test', fc.flowchart())
```

Many Markdown editors, like Typora, also support this flowchart syntax. See [the Typora documentation on flowcharts](https://support.typora.io/Draw-Diagrams-With-Markdown/#flowcharts). If you prefer the command line, try [francoislaberge/diagrams](https://github.com/francoislaberge/diagrams/#flowchart).

### Set Params to Nodes

Use the `Node.set_param(key, value)` method to attach [flowchart.js node specifiers](https://github.com/adrai/flowchart.js#node-specific-specifiers-by-type) to a node:

```
element(param1=value1,param2=value2)=>start: Start
```

There is also a shortcut for setting the `align-next=no` parameter on a `ConditionNode`:

```python
cond = ConditionNode("a cond node")
cond.no_align_next()
# or set it at construction time:
cond = ConditionNode("a cond node", align_next=False)
```

This is typically paired with a custom connection direction:

```python
cond.connect_yes(op, "right")
```

The generated flowchart DSL will look like:

```
cond(align-next=no)=>condition: Yes or No?
...
cond(yes,right)->op
```

## Python to Flowchart

PyFlowchart can also translate your Python code into flowcharts.

For example, given `simple.py`:

```python
def foo(a, b):
    if a:
        print("a")
    else:
        for i in range(3):
            print("b")
    return a + b
```

Run in the terminal:

```sh
$ python -m pyflowchart simple.py

# output flowchart code.
```

Or from Python:

```python
>>> from pyflowchart import Flowchart
>>> with open('simple.py') as f:
...     code = f.read()
...
>>> fc = Flowchart.from_code(code)
>>> print(fc.flowchart())

# output flowchart code.
```

![simple.py to flowchart](docs/imgs/py-to-flowchart.png)

## Advanced Usages

`Flowchart.from_code` is the core function for translating Python code into a flowchart:

```python
Flowchart.from_code(code, field="", inner=True, simplify=True, conds_align=False)
```

- `code`: Python source code to convert.
- `field`: Dotted path to a specific function or method (e.g. `"MyClass.my_method"`). Defaults to `""` (the entire file).
- `inner`: If `True`, parse the *body* of the field. If `False`, treat the field itself as a single node.
- `simplify`: If `True`, a one-line `if`/`loop` body is collapsed into a single node.
- `conds_align`: If `True`, consecutive `if` statements are aligned in the flowchart (horizontally or vertically, depending on the layout).

The CLI mirrors this interface:

```sh
python -m pyflowchart [-f FIELD] [-i] [--no-simplify] [--conds-align] [-o OUTPUT] code_file
```

- `-f FIELD`: Dotted path to the target field.
- `-i`: Parse the body of the field (`inner=True`).
- `--no-simplify`: Disable one-line-body simplification.
- `--conds-align`: Enable consecutive-if alignment.
- `-o OUTPUT`: Write the result to a file. Currently only `.html` / `.htm` are supported (handled by `output_html`).

### field

The `field` is the dotted path to a function (or method) you want to flowchart.

```python
# example.py
print("start")

def foo():
    foo = "foo"

class Bar():
    def buzz(self, f):
        def g(self):
            print("g")
            f(self)
        return g(self)

Bar().buzz(foo)
print("end")
```

For `example.py` above, available paths are:

- `""` (the whole file)
- `"foo"`
- `"Bar.buzz"`
- `"Bar.buzz.g"`

To generate a flowchart of `Bar.buzz.g`:

```python
# Python
from pyflowchart import Flowchart
with open('example.py') as f:
    code = f.read()
fc = Flowchart.from_code(code, field='Bar.buzz.g', inner=False)
print(fc.flowchart())
```

Or:

```sh
# CLI
python -m pyflowchart example.py -f Bar.buzz.g
```

Output result:

![specify a field](docs/imgs/field.png)

### inner

The `inner` parameter controls how the parser interprets the target field. With `inner=True`, PyFlowchart parses the *body* of the field; with `inner=False`, it treats the entire field as a single node.

![pyflowchart_inner](docs/imgs/inner.png)

In the CLI, passing `-i` sets `inner=True`; omitting `-i` means `inner=False`.

> 🔧 **For developers:** `inner=True` parses `field.body`; `inner=False` parses `[field]`.

### simplify

When `simplify=True` (the default), a one-line `if` or `loop` body is folded into the condition node itself.

```python
# example_simplify.py
a = 1
if a == 1:
    print(a)
while a < 4:
    a = a + 1
```

With `simplify=True`:

```python
flowchart = Flowchart.from_code(example_simplify_py, field="", inner=True)
print(flowchart.flowchart())
# CLI: python -m pyflowchart example_simplify.py
```

![simplify result](docs/imgs/simplify.png)

With `simplify=False`:

```python
flowchart = Flowchart.from_code(example_simplify_py, field="", inner=True, simplify=False)
print(flowchart.flowchart())
# CLI: python -m pyflowchart --no-simplify example_simplify.py
```

![no simplify result](docs/imgs/no-simplify.png)

### conds-align (Beta)

When `conds_align=True`, consecutive `if` statements are aligned in the flowchart (horizontally or vertically, depending on the layout), which often makes the resulting diagram easier to read.

```python
# example-conds-align.py
if cond1:
    op1
if cond2:
    op2
if cond3:
    op3
op_end
```

![conds-align-result](docs/imgs/conds-align.png)

**Note:** This feature is still in beta and may not work correctly in all cases.

### match-case (Python 3.10+)

PyFlowchart supports Python's structural pattern matching (`match`/`case`, introduced in Python 3.10). Each `case` branch is rendered as a condition node in the flowchart.

```python
# example_match.py
def classify(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case _:
            return "Other"
```

```sh
$ python -m pyflowchart example_match.py -f classify
```

### try/except/else/finally (Beta)

> ⚠️ **Beta feature:** `try`/`except` support is still in beta and may not work correctly in all cases.

PyFlowchart translates `try`/`except`/`else`/`finally` blocks into a structured flowchart that shows all exception-handling paths.

```python
# example_try.py
def fetch(url):
    try:
        data = requests.get(url)
    except Timeout:
        data = cached()
    except Exception as e:
        log(e)
    else:
        process(data)
    finally:
        close()
```

```sh
$ python -m pyflowchart example_try.py -f fetch
```

The generated flowchart represents the following structure:

```
[try body]
    ↓
exception raised? ──no──▶ [else body]
    │ yes                       │
    ▼                           │
except Timeout? ──yes──▶ [handler body]
    │ no                        │
except Exception as e? ──yes──▶ [handler body]
    │ no (unhandled)            │
    └──────────────────────────►┤
                                ▼
                          [finally body]
```

Each `except` clause is rendered as a condition diamond. The `else` branch is taken when no exception is raised. All paths — handled exceptions, unhandled exceptions, and the no-exception path — converge into the `finally` block. When the `try` body contains multiple statements they are folded into a single operation node so that the `exception raised?` diamond covers the whole block; for clarity it is recommended to keep `try` bodies minimal (ideally a single statement).

Python 3.11+ `except*` (ExceptionGroup) blocks are dispatched through the same mechanism.

### output html and images

Pass `-o output.html` to write the flowchart directly to an HTML file:

```sh
$ python -m pyflowchart example.py -o output.html
```

![output-html](docs/imgs/output-html.png)

Open `output.html` in your browser to visualize the flowchart. You can tweak the code and click **Run** to update the diagram. Download links for `.svg` and `.png` exports are also provided.

⚠️ The specified output file will be overwritten if it already exists.

🐍 To use this feature via Python instead of CLI, call `output_html(output_name: str, field_name: str, flowchart: str) -> None`:

```py
>>> import pyflowchart
>>> help(pyflowchart.output_html)
```

## Beautify Flowcharts

The flowcharts generated by PyFlowchart may not always look ideal. You can tweak the generated DSL directly, or simplify the original Python code to produce cleaner output. For example, removing purely defensive engineering guards (e.g. input-validation checks) that are not part of the algorithm often yields a much more readable diagram.

An example: to change the flow direction of a condition branch, add a direction specifier:

![beautify-flowchart-example](docs/imgs/beautify-example.png)

## TODOs

- [ ] Directly generate flowchart SVG/HTML:

```sh
$ pyflowchart example.py -o flowchart.svg
```

Depends on `node.js` and `flowchart.js`.

- [ ] PyFlowchart GUI

A **GUI** for PyFlowchart would be amazing. You could paste your Python code into it, and the flowchart DSL would be generated in real time, with the flowchart displayed alongside it.

- [x] Tests automation.
- [x] Chinese README.

----

Unfortunately, I am too busy (pronounced as `[ˈlеizi]`——lazy) to code these ideas myself. Please [submit an issue](https://github.com/cdfmlr/pyflowchart/issues/new) to push me on. Or, PR to make it yourself — I cannot wait to appreciate your contribution!

## References

- Inspired by [Vatsha/code_to_flowchart](https://github.com/Vatsha/code_to_flowchart)
- Based on [adrai/flowchart.js](http://flowchart.js.org), [python ast](https://docs.python.org/3/library/ast.html), [simonpercivall/astunparse](https://github.com/simonpercivall/astunparse)
- [A blog about this project](https://clownote.github.io/2020/10/24/blog/PyFlowchart/)

## License

Copyright 2020-2026 CDFMLR. All rights reserved.

Licensed under the MIT License.
