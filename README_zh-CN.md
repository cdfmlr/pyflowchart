# PyFlowchart

[English](README.md) | 机翻中文

PyFlowchart 是一个 Python 包，用于：

- 用 Python 语言编写流程图；
- 将 Python 源代码翻译成流程图。

PyFlowchart 用 [flowchart.js](https://github.com/adrai/flowchart.js) DSL 来绘制流程图，这是一种广泛使用的流程图文本表示格式。可以通过 [flowchart.js.org](http://flowchart.js.org)、[francoislaberge/diagrams](https://github.com/francoislaberge/diagrams/#flowchart) 或一些 Markdown 编辑器将这些文本转换为图片。此外，也可以直接将生成的流程图输出为可交互的 HTML 页面。

## 安装 PyFlowchart

```sh
$ pip install pyflowchart
```

## 快速开始

要将 `example.py` 中的 Python 代码流程图化，运行：

```sh
$ python -m pyflowchart example.py
# 或者，如果 pyflowchart 已加入 PATH：
$ pyflowchart example.py
```

> ⚠️ PyFlowchart 适用于 **Python 3.7+**，并在 **3.7 至 3.14** 上经过 CI 测试。要检查 Python 版本，请运行 [`python --version`](https://docs.python.org/3/using/cmdline.html#cmdoption-version)。如果同时安装了 Python 2 和 Python 3，可能需要使用 `python3` 而不是 `python`。

PyFlowchart 将把生成的 flowchart.js DSL 打印到标准输出。进入 [flowchart.js.org](http://flowchart.js.org) 或使用 [Typora](https://support.typora.io/Draw-Diagrams-With-Markdown/#flowcharts) 等编辑器，可以将输出的文本渲染成流程图。

**输出 HTML 文件：**

```sh
$ python -m pyflowchart example.py -o example.html
$ open example.html  # 或在浏览器中手动打开
```

**指定要流程图化的函数或方法：**

```sh
$ python -m pyflowchart example.py -f function_name
# 或类中的方法：
$ python -m pyflowchart example.py -f ClassName.method_name
```

例如：`python -m pyflowchart example.py -f MyClass.add`。

🎉 现在，你已经准备好享受流程图的制作了。

继续阅读本文件以了解更多用法。

## 用 Python 编写流程图

PyFlowchart 允许你用 Python 表达一个流程图，并将其翻译成 [flowchart.js](https://github.com/adrai/flowchart.js) DSL。

支持以下 [flowchart.js 节点类型](https://github.com/adrai/flowchart.js#node-types)：

- StartNode（开始节点）
- OperationNode（操作节点）
- ConditionNode（条件节点）
- InputOutputNode（输入输出节点）
- SubroutineNode（子程序节点）
- EndNode（结束节点）

节点可以通过 `connect()` 方法连接。对于 `ConditionNode`，使用 `connect_yes()` 或 `connect_no()`。`connect()` 还可以接收第二个可选参数，用于指定连线的起始方向。

用起始节点构造一个 `Flowchart` 对象，然后调用其 `flowchart()` 方法，即可获得 flowchart.js DSL：

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
sub.connect(op, "right")  # sub->op 的连线从 sub 的右侧引出
io.connect(e)

fc = Flowchart(st)
print(fc.flowchart())
```

输出：

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

访问 http://flowchart.js.org，将生成的 DSL 粘贴进去，即可渲染出 SVG 流程图：

![screenshot on flowchart.js page](docs/imgs/flowchart-js-org.png)

也可以调用 `pyflowchart.output_html` 来生成包含渲染后流程图的独立 HTML 页面：

```python
output_html('output.html', 'a_pyflow_test', fc.flowchart())
```

许多 Markdown 编辑器（例如 Typora）也支持这种流程图语法（参考：[Typora 关于流程图的文档](https://support.typora.io/Draw-Diagrams-With-Markdown/#flowcharts)）。如果你喜欢命令行，可以参考 [francoislaberge/diagrams](https://github.com/francoislaberge/diagrams/#flowchart)。

### 为节点设置参数

使用 `Node.set_param(key, value)` 方法可以为节点附加 [flowchart.js 节点限定符](https://github.com/adrai/flowchart.js#node-specific-specifiers-by-type)：

```
element(param1=value1,param2=value2)=>start: Start
```

还有一个快捷方式，用于为 `ConditionNode` 设置 `align-next=no` 参数：

```python
cond = ConditionNode("a cond node")
cond.no_align_next()
# 或者在构造时设置：
cond = ConditionNode("a cond node", align_next=False)
```

这通常与自定义连线方向配合使用：

```python
cond.connect_yes(op, "right")
```

生成的流程图 DSL 将如下所示：

```
cond(align-next=no)=>condition: Yes or No?
...
cond(yes,right)->op
```

## Python 代码转换为流程图

PyFlowchart 还可以将你的 Python 代码翻译成流程图。

例如，给定 `simple.py`：

```python
def foo(a, b):
    if a:
        print("a")
    else:
        for i in range(3):
            print("b")
    return a + b
```

在终端运行：

```sh
$ python -m pyflowchart simple.py

# 输出流程图代码
```

或者在 Python 中：

```python
>>> from pyflowchart import Flowchart
>>> with open('simple.py') as f:
...     code = f.read()
...
>>> fc = Flowchart.from_code(code)
>>> print(fc.flowchart())

# 输出流程图代码
```

![simple.py to flowchart](docs/imgs/py-to-flowchart.png)

## 进阶用法

`Flowchart.from_code` 是将 Python 代码转换为流程图的核心函数：

```python
Flowchart.from_code(code, field="", inner=True, simplify=True, conds_align=False)
```

- `code`: 要转换的 Python 源代码。
- `field`: 目标函数或方法的点分路径（例如 `"MyClass.my_method"`）。默认为 `""`（整个文件）。
- `inner`: 若为 `True`，解析 field 的*函数体*；若为 `False`，将整个 field 作为单一节点处理。
- `simplify`: 若为 `True`，只有一行函数体的 `if`/循环语句会被折叠成单一节点。
- `conds_align`: 若为 `True`，连续的 `if` 语句会在流程图中对齐排列（水平或垂直，取决于布局）。

CLI 与此函数一一对应：

```sh
python -m pyflowchart [-f FIELD] [-i] [--no-simplify] [--conds-align] [-o OUTPUT] code_file
```

- `-f FIELD`: 目标 field 的点分路径。
- `-i`: 解析 field 的函数体（`inner=True`）。
- `--no-simplify`: 禁用单行函数体简化。
- `--conds-align`: 启用连续 if 语句对齐排列。
- `-o OUTPUT`: 将结果写入文件。目前仅支持 `.html` / `.htm`（由 `output_html` 处理）。

### field

`field` 是你想要流程图化的函数（或方法）的点分路径：

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

对于上面的 `example.py`，可用的路径有：

- `""` （整个文件）
- `"foo"`
- `"Bar.buzz"`
- `"Bar.buzz.g"`

如果要生成 `Bar.buzz.g` 的流程图：

```python
# Python
from pyflowchart import Flowchart
with open('example.py') as f:
    code = f.read()
fc = Flowchart.from_code(code, field='Bar.buzz.g', inner=False)
print(fc.flowchart())
```

或者：

```sh
# CLI
python -m pyflowchart example.py -f Bar.buzz.g
```

输出结果：

![specify a field](docs/imgs/field.png)

### inner

`inner` 控制解析器对目标 field 的解读方式。`inner=True` 时，PyFlowchart 解析 field 的*函数体*；`inner=False` 时，将整个 field 作为单一节点。

![pyflowchart_inner](docs/imgs/inner.png)

在 CLI 中，添加 `-i` 参数意味着 `inner=True`，否则为 `inner=False`。

> 🔧 **开发者注：** `inner=True` 解析 `field.body`；`inner=False` 解析 `[field]`。

### simplify

`simplify=True`（默认值）时，只有一行函数体的 `if` 或循环语句会被折叠进条件节点本身。

```python
# example_simplify.py
a = 1
if a == 1:
    print(a)
while a < 4:
    a = a + 1
```

`simplify=True` 时：

```python
flowchart = Flowchart.from_code(example_simplify_py, field="", inner=True)
print(flowchart.flowchart())
# CLI: python -m pyflowchart example_simplify.py
```

![simplify result](docs/imgs/simplify.png)

`simplify=False` 时：

```python
flowchart = Flowchart.from_code(example_simplify_py, field="", inner=True, simplify=False)
print(flowchart.flowchart())
# CLI: python -m pyflowchart --no-simplify example_simplify.py
```

![no simplify result](docs/imgs/no-simplify.png)

### conds-align（Beta）

`conds_align=True` 时，连续的 `if` 语句会在流程图中对齐排列（水平或垂直，取决于布局），通常能让图表更易读。

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

**注意：** 此功能仍处于 Beta 阶段，在某些情况下可能无法正常工作。

### match-case（Python 3.10+）

PyFlowchart 支持 Python 3.10 引入的结构化模式匹配（`match`/`case`）。每个 `case` 分支会被渲染为流程图中的一个条件节点。

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

### try/except/else/finally（Beta）

> ⚠️ **Beta 功能：** `try`/`except` 支持仍处于测试阶段，在某些情况下可能无法正常工作。

PyFlowchart 将 `try`/`except`/`else`/`finally` 语句块翻译为结构化流程图，呈现所有异常处理路径。

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

生成的流程图结构如下：

```
[try 语句体]
    ↓
是否发生异常？──否──▶ [else 语句体]
    │ 是                    │
    ▼                       │
except Timeout？──是──▶ [处理代码]
    │ 否                    │
except Exception as e？──是──▶ [处理代码]
    │ 否（未处理）           │
    └──────────────────────►┤
                            ▼
                      [finally 语句体]
```

每个 `except` 子句被渲染为一个条件菱形节点。当没有异常被触发时，走 `else` 分支。无论是已处理异常、未处理异常还是无异常路径，最终都会汇聚到 `finally` 块。当 `try` 语句体包含多条语句时，它们会被折叠为单一操作节点，以确保整个语句块都被 `exception raised?` 菱形覆盖；为保持清晰，建议尽量保持 `try` 语句体简短（最理想是只有一条语句）。

Python 3.11+ 的 `except*`（ExceptionGroup）块也通过相同机制处理。

### 输出 HTML 与图片

传入 `-o output.html` 可将流程图直接写入 HTML 文件：

```sh
$ python -m pyflowchart example.py -o output.html
```

![output-html](docs/imgs/output-html.png)

在浏览器中打开 `output.html` 即可可视化流程图。你可以修改代码并点击 **Run** 更新图表，还提供了 `.svg` 和 `.png` 的下载链接。

⚠️ 指定的输出文件如果已存在，将会被覆盖。

🐍 如需通过 Python 而非 CLI 使用此功能，调用 `output_html(output_name: str, field_name: str, flowchart: str) -> None`：

```py
>>> import pyflowchart
>>> help(pyflowchart.output_html)
```

## 美化生成的流程图

有时，生成的流程图效果不够理想。这种情况下，建议直接修改生成的 DSL，或者精简原始 Python 代码以获得更清晰的输出。例如，去掉那些在算法上无关紧要的防御性工程代码（如输入校验），往往能让流程图更简洁易读。

（流程图应当用来表示算法，而不是具体实现。算法是给人看的，实现是给机器看的。我推荐在生成流程图之前，去掉那些在实践上举足轻重、但在算法上细枝末节的代码。）

示例：若不喜欢条件分支的流向，可以为连接添加方向限定符：

![beautify-flowchart-example](docs/imgs/beautify-example.png)

## TODOs

- [ ] 直接生成流程图的 SVG/HTML：

```sh
$ pyflowchart example.py -o flowchart.svg
```

这需要依赖 `node.js` 和 `flowchart.js`。

- [ ] PyFlowchart GUI

如果能写一个 PyFlowchart 的 **GUI** 就太棒了——把代码粘贴进去，流程图 DSL 实时生成，流程图也显示在一旁，非常方便。

- [x] 自动化测试。
- [x] 中文 README。

----

遗憾的是，我太忙了（写作"忙碌"，读作"懒惰"），无法马上实现这些想法。如果你对包括但不限于这里列出的功能有所期待，请务必 [提交一个 Issue](https://github.com/cdfmlr/pyflowchart/issues/new) 来推动我。或者，直接 PR，我已经迫不及待地想欣赏你的杰出贡献了！

## References

- Inspired by [Vatsha/code_to_flowchart](https://github.com/Vatsha/code_to_flowchart)
- Based on [adrai/flowchart.js](http://flowchart.js.org), [python ast](https://docs.python.org/3/library/ast.html), [simonpercivall/astunparse](https://github.com/simonpercivall/astunparse)
- [A blog about this project](https://clownote.github.io/2020/10/24/blog/PyFlowchart/)

## License

Copyright 2020-2026 CDFMLR. All rights reserved.

Licensed under the MIT License.
