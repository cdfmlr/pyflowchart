# PyFlowchart

PyFlowchart is a package to:

- write flowchart in Python,
- translate Python source codes into flowchart.

PyFlowchart produces flowcharts in [flowchart.js](https://github.com/adrai/flowchart.js) flowchart DSL, a widely used flow chart textual representation. It's easy to convert these flowcharts text into a picture via [flowchart.js.org](http://flowchart.js.org), [francoislaberge/diagrams](https://github.com/francoislaberge/diagrams/#flowchart), or some markdown editors. 

## Get PyFlow

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

## Beautify Flowcharts

Modify the generated flowchart code by yourself.

## Reference

- Inspired by [Vatsha/code_to_flowchart](https://github.com/Vatsha/code_to_flowchart)
- Based on [adrai/flowchart.js](http://flowchart.js.org), [python ast](https://docs.python.org/3/library/ast.html), [simonpercivall/astunparse](https://github.com/simonpercivall/astunparse)
- [A blog about this project](https://clownote.github.io/2020/10/24/blog/PyFlowchart/)

## License

Copyright 2020 CDFMLR. All rights reserved.

Licensed under the MIT License.

