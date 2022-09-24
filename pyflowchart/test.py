"""
Simple tests for dev.

I have no idea about how to unit test a compiler-like stuff.
Forgive my fool tests.

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""

import _ast
import ast
import re
import unittest

import astunparse

from pyflowchart.ast_node import *
from pyflowchart.flowchart import *


def flowchart_translate_test(name='flowchart test'):
    st = StartNode('start')
    op = OperationNode('operation:' + name)
    cond = ConditionNode('condition')
    io = InputOutputNode(InputOutputNode.OUTPUT, 'output')
    e = EndNode('end')

    st.connect(op)
    op.connect(cond)
    cond.connect_yes(io)
    cond.connect_no(op)
    io.connect(e)

    fc = Flowchart(st)
    return fc.flowchart()


EXPECTED_FLOWCHART_TRANSLATE_TEST = '''
st0=>start: start start
op1=>operation: operation:flowchart test
cond2=>condition: condition
io3=>inputoutput: output: output
e4=>end: end end

st0->op1
op1->cond2
cond2->
cond2->
cond2(yes)->io3
io3->e4
cond2(no)->op1
'''


# deprecated
def ast_unparser_test():
    expr = ''
    with open('./test.py') as f:
        expr = f.read()
    expr_ast = ast.parse(expr)
    u = astunparse.unparse(expr_ast)
    return u


# deprecated
def ast_node_test():
    expr = ''
    with open('./test.py') as f:
        expr = f.read()
    expr_ast = ast.parse(expr)
    for b in expr_ast.body:
        if isinstance(b, _ast.FunctionDef):
            st = FunctionDefStart(b)
            arg = FunctionDefArgsInput(b)
            e = FunctionDefEnd(b)

            st.connect(arg)
            arg.connect(e)

            flow = Flowchart(st).flowchart()
            print(flow)
            break


def seq_test():
    expr = '''
a()
b = 1
print(c)
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_SEQ_TEST = '''
sub2=>subroutine: a()
op4=>operation: b = 1
sub6=>subroutine: print(c)

sub2->op4
op4->sub6
'''


def loop_test():
    expr = '''
start()
while a < 0:
    print('a<0')
    for i in range(10):
        ir()
    for j in range(9):
        break
print('end')
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_LOOP_TEST = '''
sub2=>subroutine: start()
cond5=>condition: while (a < 0)
sub37=>subroutine: print('a<0')
cond40=>operation: ir() while  i in range(10)
cond53=>condition: for j in range(9)
sub60=>subroutine: break
sub66=>subroutine: print('end')

sub2->cond5
cond5(yes)->sub37
sub37->cond40
cond40->cond53
cond53(yes)->sub60
cond53(no)->cond5
cond5(no)->sub66
'''


def if_test():
    expr = '''
if a > 0:
    if b > 0:
        print('ab')
        if c > 0:
            cgz()
        else:
            clez()
            if d > 0:
                if e > 0:
                    print('777777')
    print('abc')
else:
    alez()
end_of_ifs()
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_IF_TEST = '''
cond3=>condition: if (a > 0)
cond8=>condition: if (b > 0)
sub12=>subroutine: print('ab')
cond15=>condition: if (c > 0)
sub19=>subroutine: cgz()
sub48=>subroutine: print('abc')
sub55=>subroutine: end_of_ifs()
sub23=>subroutine: clez()
cond26=>condition: if (d > 0)
cond31=>operation: print('777777') if  (e > 0)
sub52=>subroutine: alez()

cond3(yes)->cond8
cond8(yes)->sub12
sub12->cond15
cond15(yes)->sub19
sub19->sub48
sub48->sub55
cond15(no)->sub23
sub23->cond26
cond26(yes)->cond31
cond31->sub48
cond26(no)->sub48
cond8(no)->sub48
cond3(no)->sub52
sub52->sub55
'''


def cond_loop_test():
    expr = '''
start()
r = randint(100)
a, m, b = 0, 50, 100
while m != r:
    m = (a + b) / 2
    if m > r:
        a = m
    elif m < r:
        b = m
print(m)
end()
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_COND_LOOP_TEST = '''
sub2=>subroutine: start()
op4=>operation: r = randint(100)
op6=>operation: (a, m, b) = (0, 50, 100)
cond9=>condition: while (m != r)
op37=>operation: m = ((a + b) / 2)
cond40=>condition: if (m > r)
op44=>operation: a = m
cond49=>operation: b = m if  (m < r)
sub62=>subroutine: print(m)
sub64=>subroutine: end()

sub2->op4
op4->op6
op6->cond9
cond9(yes)->op37
op37->cond40
cond40(yes)->op44
op44->cond9
cond40(no)->cond49
cond49->cond9
cond9(no)->sub62
sub62->sub64
'''


def func_test():
    expr = '''
def Lagrange(points, simplify_result=True, verbose=False):
    x = Symbol('x')
    L = 0  # interpolated polynomial
    for i, point in enumerate(points):
        xi, yi = point
        li = 1
        for j in range(len(points)):
            if j == i:
                continue
            xj, yj = points[j]
            li *= (x - xj) / (xi - xj)
        L += yi * li
        if verbose:
            print(f"l_{i}(x) = ", simplify(yi * li))

    if simplify_result:
        L = simplify(L)
    return L
    '''
    #     expr = '''
    # def func(a, b):
    #     def nested(c):
    #         if c:
    #             return c()
    #         raise ValueError()
    #     if a > b:
    #         return a
    #     print('b')
    #     '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_FUNC_TEST = '''
st3=>start: start Lagrange
io5=>inputoutput: input: points, simplify_result, verbose
op8=>operation: x = Symbol('x')
op10=>operation: L = 0
cond13=>condition: for (i, point) in enumerate(points)
op73=>operation: (xi, yi) = point
op75=>operation: li = 1
cond78=>condition: for j in range(len(points))
cond99=>operation: continue if  (j == i)
op109=>operation: (xj, yj) = points[j]
op111=>operation: li *= ((x - xj) / (xi - xj))
op115=>operation: L += (yi * li)
cond118=>operation: print(f'l_{i}(x) = ', simplify((yi * li))) if  verbose
cond131=>operation: L = simplify(L) if  simplify_result
io144=>inputoutput: output:  L
e142=>end: end function return

st3->io5
io5->op8
op8->op10
op10->cond13
cond13(yes)->op73
op73->op75
op75->cond78
cond78(yes)->cond99
cond99->op109
op109->op111
op111(left)->cond78
cond78(no)->op115
op115->cond118
cond118->cond13
cond13(no)->cond131
cond131->io144
io144->e142
'''


def from_code_test():
    code = '''
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
    '''
    # should test:
    # field="NOTEXIST", field=".", field="Bar.", field="Bar.NOTEXIST"
    # no field, field="", field="Bar.buzz", field="Bar.buzz.g"
    flowchart = Flowchart.from_code(code, field="Bar.buzz", inner=True)
    return flowchart.flowchart()


EXPECTED_FROM_CODE_TEST = '''
st3=>start: start g
io5=>inputoutput: input: self
sub8=>subroutine: print('g')
sub10=>subroutine: f(self)
e12=>end: end g
io18=>inputoutput: output:  g(self)
e16=>end: end function return

st3->io5
io5->sub8
sub8->sub10
sub10->e12
e12->io18
io18->e16
'''


# deprecated
def simplify_on_off():
    code = '''
a = 1
if a == 1:
    print(a)
while a < 4:
    a = a + 1
    '''
    print("------(default) simplify=True:")
    flowchart = Flowchart.from_code(code, field="", inner=True)
    print(flowchart.flowchart())

    print("------simplify=False:")
    flowchart = Flowchart.from_code(code, field="", inner=True, simplify=False)
    print(flowchart.flowchart())


SIMPLIFY_TEST_CODE = '''
a = 1
if a == 1:
    print(a)
while a < 4:
    a = a + 1
'''


def simplify_off_test():
    code = SIMPLIFY_TEST_CODE
    flowchart = Flowchart.from_code(code, field="", inner=True, simplify=False)
    return flowchart.flowchart()


def simplify_on_test():
    code = SIMPLIFY_TEST_CODE
    flowchart = Flowchart.from_code(code, field="", inner=True)
    return flowchart.flowchart()


EXPECTED_SIMPLIFY_OFF_TEST = '''
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
'''

EXPECTED_SIMPLIFY_ON_TEST = '''
op2=>operation: a = 1
cond5=>operation: print(a) if  (a == 1)
cond16=>operation: a = (a + 1) while  (a < 4)

op2->cond5
cond5->cond16
'''


class PyflowchartTestCase(unittest.TestCase):
    def assertEqualFlowchart(self, got: str, expected: str):
        return self.assertEqual(
            self._fmt_flowchart(got),
            self._fmt_flowchart(expected))

    @staticmethod
    def _fmt_flowchart(flowchart: str):
        flowchart = flowchart.strip()
        # ignores node id
        flowchart = re.sub(r'\d+', '*', flowchart)
        return flowchart

    def test_flowchart_translate(self):
        got = flowchart_translate_test()
        self.assertEqualFlowchart(got, EXPECTED_FLOWCHART_TRANSLATE_TEST)

    def test_seq(self):
        got = seq_test()
        self.assertEqualFlowchart(got, EXPECTED_SEQ_TEST)

    def test_loop(self):
        got = loop_test()
        self.assertEqualFlowchart(got, EXPECTED_LOOP_TEST)

    def test_if(self):
        got = if_test()
        self.assertEqualFlowchart(got, EXPECTED_IF_TEST)

    def test_cond_loop(self):
        got = cond_loop_test()
        self.assertEqualFlowchart(got, EXPECTED_COND_LOOP_TEST)

    def test_func(self):
        got = func_test()
        self.assertEqualFlowchart(got, EXPECTED_FUNC_TEST)

    def test_from_code(self):
        got = from_code_test()
        self.assertEqualFlowchart(got, EXPECTED_FROM_CODE_TEST)

    def test_simplify_off(self):
        got = simplify_off_test()
        self.assertEqualFlowchart(got, EXPECTED_SIMPLIFY_OFF_TEST)

    def test_simplify_on(self):
        got = simplify_on_test()
        self.assertEqualFlowchart(got, EXPECTED_SIMPLIFY_ON_TEST)


if __name__ == '__main__':
    # print(flowchart_translate_test())
    # print(ast_unparser_test())
    # ast_node_test()
    # print(seq_test())
    # print(loop_test())
    # print(if_test())
    # print(cond_loop_test())
    # print(func_test())
    # print(from_code_test())
    # print(simplify_off_test())
    # print(simplify_on_test())
    # simplify_on_off()
    unittest.main()
