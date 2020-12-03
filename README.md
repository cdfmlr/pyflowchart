# PyFlowchart

PyFlowchart is a package to:

- write flowchart in Python,
- translate Python source codes into flowchart.

PyFlowchart produces flowcharts in [flowchart.js](https://github.com/adrai/flowchart.js) flowchart DSL, a widely used flow chart textual representation. It's easy to convert these flowcharts text into a picture via [flowchart.js.org](http://flowchart.js.org), [francoislaberge/diagrams](https://github.com/francoislaberge/diagrams/#flowchart), or some markdown editors. 

## Get PyFlowchart

```sh
$ pip3 install pyflowchart
```

## Flowchart in Python

PyFlowchart including [flowchart.js](https://github.com/adrai/flowchart.js#node-types) node types:

- StartNode
- OperationNode
- ConditionNode
- InputOutputNode
- SubroutineNode
- EndNode

Nodes can be connected by `connect()` method (`connect_{yes|no}` for ConditionNode).

Get a Flowchart with your start node and call its `flowchart()` method to generate flowchart.js flowchart DSL：

```python
from pyflowchart import *

st = StartNode('a_pyflow_test')
op = OperationNode('do something')
cond = ConditionNode('Yes or No?')
io = InputOutputNode(InputOutputNode.OUTPUT, 'something...')
sub = SubroutineNode('A Subroutine')
e = EndNode('a_pyflow_test')

# define the direction the connection will leave the node from
sub.set_connect_direction("right")
    
st.connect(op)
op.connect(cond)
cond.connect_yes(io)
cond.connect_no(sub)
sub.connect(op)
io.connect(e)
 
fc = Flowchart(st)
print(fc.flowchart())
```

Output:

```
st4471442960=>start: start a_pyflow_test
op4471442064=>operation: do something
cond4471501392=>condition: Yes or No?
io4471501648=>inputoutput: output: something...
e4471501904=>end: end a_pyflow_test
sub4471501584=>subroutine: A Subroutine

st4471442960->op4471442064
op4471442064->cond4471501392
cond4471501392(yes)->io4471501648
io4471501648->e4471501904
cond4471501392(no)->sub4471501584
sub4471501584(right)->op4471442064
```

Go http://flowchart.js.org and translate the generated textual representation into SVG flow chart diagrams:

![screenshot on flowchart.js page](https://tva1.sinaimg.cn/large/0081Kckwly1gjzforbn9vj30z00lv12f.jpg)

P.S. Many Markdown editors (for example, Typora) support this flowchart syntax, too. And if you prefer CLI, see [francoislaberge/diagrams](https://github.com/francoislaberge/diagrams/#flowchart).

## Python to Flowchart

PyFlowchart can also translate your Python Codes into Flowcharts.

For example, you got a `simple.py`:

```python
def foo(a, b):
    if a:
        print("a")
    else:
        for i in range(3):
            print("b")
    return a + b
```

Run PyFlowchart in CLI to generate flowchart code:

```sh
$ python3 -m pyflowchart simple.py

# output flowchart code.
```

Or, in Python

```python
>>> from pyflowchart import Flowchart
>>> with open('simple.py') as f:
...     code = f.read()
... 
>>> fc = Flowchart.from_code(code)
>>> print(fc.flowchart())

# output flowchart code.
```

![result](https://tva1.sinaimg.cn/large/0081Kckwly1gjzgay3158j30py0gj442.jpg)

## Advanced Usages

- Specify a field of code to generate flowchart (new feature: v0.1.0)

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

To generate a flowchart of `Bar.buzz.g`：

```python
# Python
from pyflowchart import Flowchart
with open('example.py') as f:
	code = f.read()
fc = Flowchart.from_code(code, field='Bar.buzz.g', inner=False)
print(fc.flowchart())
```

```sh
# CLI
python3 -m pyflowchart example.py -f Bar.buzz.g
```

Output result:

![result](https://tva1.sinaimg.cn/large/0081Kckwly1gl9wdmg9sij30it07xgnm.jpg)


The `from_code` is defined as:

```python
Flowchart.from_code(code, field='', inner=True)
```

PyFlowchart CLI is a interface for this function:

```sh
python3 -m pyflowchart [-h] [-f FIELD] [-i] code_file
```

### field

`field` is the path to a field (i.e. a function) you want to draw flowchart. For `example.py` above, available paths are:

    - "" (means the whole code)
    - "foo"
    - "Bar.buzz"
    - "Bar.buzz.g"

### inner

`inner` controls parser's behaves. Techly, `inner=True` means parsing `field.body`, while `inner=False` parses `[field]`. So, if  `inner=True`, pyflowchart will look into the field, otherwise  it takes field as a node.

![pyflowchart_inner](https://tva1.sinaimg.cn/large/0081Kckwly1gl9xf1uo5fj31d30jr78m.jpg)

For CLI,  adding an argument `-i`  means `inner=True`, else `inner=False`.

## Beautify Flowcharts

Modify the generated flowchart code by yourself.

## TODO

- [ ] Generate flowchart SVG/HTML.

```sh
$ pyflowchart example.py -o flowchart.svg
```

Depends node.js and flowchart.js.

- [ ] PyFlowchart GUI

Well, I guess a **GUI** for PyFlowchart may be remarkable. Pasting your code into it, the flowchart DSL will be generated just in time, and flowchart will be shown aside.

- [ ] The Chinese README your buddies waiting for!

----

Sadly, I am too busy (this word is pronounced as `[ˈlеizi]`——lazy) to code these ideas. Please [submit an issue](https://github.com/cdfmlr/pyflowchart/issues/new) to push me on. Or, PR to make it by yourself. I cannot wait to appreciate your great contribution!

## References

- Inspired by [Vatsha/code_to_flowchart](https://github.com/Vatsha/code_to_flowchart)
- Based on [adrai/flowchart.js](http://flowchart.js.org), [python ast](https://docs.python.org/3/library/ast.html), [simonpercivall/astunparse](https://github.com/simonpercivall/astunparse)
- [A blog about this project](https://clownote.github.io/2020/10/24/blog/PyFlowchart/)

## License

Copyright 2020 CDFMLR. All rights reserved.

Licensed under the MIT License.

