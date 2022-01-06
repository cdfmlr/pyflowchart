Examples in the README and generated flowchart codes.

## PyFlowchart

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

result:

```flow
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

## simple.py


```python
def foo(a, b):
    if a:
        print("a")
    else:
        for i in range(3):
            print("b")
    return a + b
```

result:

```flow
st3=>start: start foo
io5=>inputoutput: input: a, b
cond9=>condition: if a
sub13=>subroutine: print('a')
io34=>inputoutput: output:  (a + b)
e32=>end: end function return
cond18=>operation: print('b') while  i in range(3)

st3->io5
io5->cond9
cond9(yes)->sub13
sub13->io34
io34->e32
cond9(no)->cond18
cond18->io34
```

## example_field.py

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

result:

```flow
st3=>start: start g
io5=>inputoutput: input: self
sub8=>subroutine: print('g')
sub10=>subroutine: f(self)
e12=>end: end g

st3->io5
io5->sub8
sub8->sub10
sub10->e12
```

## example_simplify.py

```python
# example_simplify.py
a = 1
if a == 1:
    print(a)
while a < 4:
    a = a + 1
```

result(simplify=True):

```flow
op2=>operation: a = 1
cond5=>operation: print(a) if  (a == 1)
cond16=>operation: a = (a + 1) while  (a < 4)

op2->cond5
cond5->cond16
```

result(simplify=False):

```flow
op2=>operation: a = 1
cond5=>condition: if (a == 1)
sub9=>subroutine: print(a)
cond15=>condition: while (a < 4)
op22=>operation: a = (a + 1)

op2->cond5
cond5(yes)->sub9
sub9->cond15
cond15(yes)->op22
op22(left)->cond15
cond5(no)->cond15
```
