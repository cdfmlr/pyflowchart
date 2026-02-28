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
import warnings

from pyflowchart.ast_node import *
from pyflowchart.flowchart import *

# import astunparse # https://github.com/cdfmlr/pyflowchart/issues/28
import sys

if sys.version_info < (3, 9):
    import astunparse
else:
    import ast as astunparse


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


def match_test():
    if sys.version_info < (3, 10):
        warnings.warn("match test requires python >= 3.10")
        return ''
    expr = '''
def test_match(a, b, c):
    if a > 0:
        match b:
            case 1:
                print('ab')
            case 2:
                print('abc')
                c = 1 + b + a
            case 3:
                print('nested match')
                match c:
                    case["a"]:
                        print('a')
                    case["a", *other_items]:
                        print('a and others')
                    case[*first_items, "d"] | (*first_items, "d"):
                        print('d is the last item')
            case _:
                print('abcd')
        end_of_match()
    else:
        alez()
    end_of_ifs()
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_MATCH_TEST_PY_GE_310 = '''
st3=>start: start test_match
io5=>inputoutput: input: a, b, c
cond9=>condition: if a > 0
cond16=>condition: if b match case 1
sub20=>subroutine: print('ab')
cond25=>condition: if b match case 2
sub29=>subroutine: print('abc')
op31=>operation: c = 1 + b + a
cond36=>condition: if b match case 3
sub40=>subroutine: print('nested match')
cond45=>condition: if c match case ['a']
sub49=>subroutine: print('a')
cond54=>condition: if c match case ['a', *other_items]
sub58=>subroutine: print('a and others')
cond63=>condition: if c match case [*first_items, 'd'] | [*first_items, 'd']
sub67=>subroutine: print('d is the last item')
cond75=>condition: if b match case _
sub79=>subroutine: print('abcd')
sub84=>subroutine: end_of_match()
sub91=>subroutine: end_of_ifs()
e93=>end: end test_match
sub88=>subroutine: alez()

st3->io5
io5->cond9
cond9(yes)->cond16
cond16(yes)->sub20
sub20->cond25
cond25(yes)->sub29
sub29->op31
op31->cond36
cond36(yes)->sub40
sub40->cond45
cond45(yes)->sub49
sub49->cond54
cond54(yes)->sub58
sub58->cond63
cond63(yes)->sub67
sub67->cond75
cond75(yes)->sub79
sub79->sub84
sub84->sub91
sub91->e93
cond75(no)->sub84
cond63(no)->cond75
cond54(no)->cond63
cond45(no)->cond54
cond36(no)->cond75
cond25(no)->cond36
cond16(no)->cond25
cond9(no)->sub88
sub88->sub91
'''


def async_func_test():
    expr = '''
async def fetch(url, retries=3):
    result = await get(url)
    return result
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_ASYNC_FUNC_TEST = '''
st3=>start: start fetch
io5=>inputoutput: input: url, retries
op8=>operation: result = await get(url)
io13=>inputoutput: output:  result
e11=>end: end function return

st3->io5
io5->op8
op8->io13
io13->e11
'''


def async_for_test():
    expr = '''
async for item in aiter():
    print(item)
    process(item)
done()
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_ASYNC_FOR_TEST = '''
cond3=>condition: async for item in aiter()
sub12=>subroutine: print(item)
sub14=>subroutine: process(item)
sub18=>subroutine: done()

cond3(yes)->sub12
sub12->sub14
sub14(left)->cond3
cond3(no)->sub18
'''


def raise_test():
    expr = '''
x = 1
raise ValueError('oops')
y = 2
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_RAISE_TEST = '''
op2=>operation: x = 1
sub4=>subroutine: raise ValueError('oops')

op2->sub4
'''


def yield_from_test():
    expr = '''
def gen(n):
    yield from range(n)
    yield from [1, 2, 3]
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_YIELD_FROM_TEST = '''
st11=>start: start gen
io13=>inputoutput: input: n
io16=>inputoutput: output: yield from range(n)
io18=>inputoutput: output: yield from [1, 2, 3]
e20=>end: end gen

st11->io13
io13->io16
io16->io18
io18->e20
'''


def try_test():
    expr = '''
try:
    risky_op()
except ValueError:
    handle()
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_TRY_TEST = '''
sub5=>subroutine: risky_op()
cond2=>condition: exception raised?
cond7=>condition: except ValueError
sub11=>subroutine: handle()

sub5->cond2
cond2(yes)->cond7
cond7(yes)->sub11
'''


def try_finally_test():
    expr = '''
try:
    risky_op()
finally:
    cleanup()
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_TRY_FINALLY_TEST = '''
sub21=>subroutine: risky_op()
cond18=>condition: exception raised?
sub27=>subroutine: cleanup()

sub21->cond18
cond18(yes)->sub27
cond18(no)->sub27
'''


def try_full_test():
    """try / multiple except / else / finally — all four clauses present."""
    expr = '''
try:
    result = fetch()
except Timeout:
    result = cached()
except Exception as e:
    log(e)
else:
    process(result)
finally:
    close()
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_TRY_FULL_TEST = '''
op5=>operation: result = fetch()
cond2=>condition: exception raised?
cond7=>condition: except Timeout
op11=>operation: result = cached()
sub26=>subroutine: close()
cond13=>condition: except Exception as e
sub17=>subroutine: log(e)
sub22=>subroutine: process(result)

op5->cond2
cond2(yes)->cond7
cond7(yes)->op11
op11->sub26
cond7(no)->cond13
cond13(yes)->sub17
sub17->sub26
cond13(no)->sub26
cond2(no)->sub22
sub22->sub26
'''


def try_in_sequence_test():
    """do something -> try block -> other things (try is not the only statement)."""
    expr = '''
prepare()
try:
    result = fetch()
except IOError:
    result = default()
use(result)
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_TRY_IN_SEQUENCE_TEST = '''
sub30=>subroutine: prepare()
op35=>operation: result = fetch()
cond32=>condition: exception raised?
cond37=>condition: except IOError
op41=>operation: result = default()
sub46=>subroutine: use(result)

sub30->op35
op35->cond32
cond32(yes)->cond37
cond37(yes)->op41
op41->sub46
cond37(no)->sub46
cond32(no)->sub46
'''


def try_in_loop_test():
    """try/except nested inside a for loop."""
    expr = '''
for item in items:
    try:
        process(item)
    except ValueError:
        skip(item)
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_TRY_IN_LOOP_TEST = '''
cond51=>condition: for item in items
sub58=>subroutine: process(item)
cond55=>condition: exception raised?
cond60=>condition: except ValueError
sub64=>subroutine: skip(item)

cond51(yes)->sub58
sub58->cond55
cond55(yes)->cond60
cond60(yes)->sub64
sub64->cond51
cond60(no)->cond51
cond55(no)->cond51
'''


def try_multiline_body_test():
    """Multiple statements in the try body are folded into a single operation node.

    All statements in the try body are joined into one OperationNode so that
    the "exception raised?" condition covers the entire block, not just the
    last statement.
    """
    expr = '''
try:
    a = setup()
    b = process(a)
    c = finalize(b)
except ValueError:
    handle()
    '''
    expr_ast = ast.parse(expr)
    p = parse(expr_ast.body)
    flow = Flowchart(p.head).flowchart()
    return flow


EXPECTED_TRY_MULTILINE_BODY_TEST = '''
op3=>operation: a = setup()
b = process(a)
c = finalize(b)
cond2=>condition: exception raised?
cond5=>condition: except ValueError
sub9=>subroutine: handle()

op3->cond2
cond2(yes)->cond5
cond5(yes)->sub9
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

        # ignores brackets
        flowchart_updated = ''
        for line in flowchart.splitlines():
            parts = line.split(':')
            for i in range(1, len(parts)):
                parts[i] = parts[i].replace('(', ' ')
                parts[i] = parts[i].replace(')', ' ')
            line = ':'.join(parts)
            flowchart_updated += line + '\n'
        flowchart = flowchart_updated

        # multiple spaces to one
        flowchart = re.sub(r'[\t\s]+', r' ', flowchart)

        return flowchart

    def test_flowchart_translate(self):
        got = flowchart_translate_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_FLOWCHART_TRANSLATE_TEST)

    def test_seq(self):
        got = seq_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_SEQ_TEST)

    def test_loop(self):
        got = loop_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_LOOP_TEST)

    def test_if(self):
        got = if_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_IF_TEST)

    def test_cond_loop(self):
        got = cond_loop_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_COND_LOOP_TEST)

    def test_func(self):
        got = func_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_FUNC_TEST)

    def test_from_code(self):
        got = from_code_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_FROM_CODE_TEST)

    def test_simplify_off(self):
        got = simplify_off_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_SIMPLIFY_OFF_TEST)

    def test_simplify_on(self):
        got = simplify_on_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_SIMPLIFY_ON_TEST)

    def test_match(self):
        if sys.version_info < (3, 10):
            warnings.warn("match test requires python >= 3.10")
            return
        got = match_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_MATCH_TEST_PY_GE_310)

    def test_async_func(self):
        got = async_func_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_ASYNC_FUNC_TEST)

    def test_async_for(self):
        got = async_for_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_ASYNC_FOR_TEST)

    def test_raise(self):
        got = raise_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_RAISE_TEST)

    def test_yield_from(self):
        got = yield_from_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_YIELD_FROM_TEST)

    def test_try(self):
        got = try_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_TRY_TEST)

    def test_try_finally(self):
        got = try_finally_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_TRY_FINALLY_TEST)

    def test_try_full(self):
        """try with multiple except handlers, an else clause, and finally."""
        got = try_full_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_TRY_FULL_TEST)

    def test_try_in_sequence(self):
        """try block is preceded and followed by other statements."""
        got = try_in_sequence_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_TRY_IN_SEQUENCE_TEST)

    def test_try_in_loop(self):
        """try/except nested inside a for loop."""
        got = try_in_loop_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_TRY_IN_LOOP_TEST)

    def test_try_multiline_body(self):
        """Multiple statements in try body are folded into a single node."""
        got = try_multiline_body_test()
        print(got)
        self.assertEqualFlowchart(got, EXPECTED_TRY_MULTILINE_BODY_TEST)

    # ------------------------------------------------------------------ #
    #  Tests for bug fixes                                                 #
    # ------------------------------------------------------------------ #

    def test_invalid_field_raises(self):
        """from_code() must raise ValueError (not AssertionError) for a field
        that does not exist in the given code.  Previously this was an assert
        that was silently skipped under ``python -O``.
        """
        code = 'def foo(): pass'
        with self.assertRaises(ValueError):
            Flowchart.from_code(code, field='nonexistent')

    def test_empty_code_raises(self):
        """from_code() must raise ValueError when the parsed body is empty."""
        with self.assertRaises(ValueError):
            Flowchart.from_code('', field='', inner=True)

    def test_find_field_invalid(self):
        """find_field_from_ast() must return an AST node whose body is []
        for a field path that does not exist.  This exercises the control-flow
        branch that previously relied on a bare ``assert`` (broken under -O).
        """
        code_ast = ast.parse('def foo(): pass')
        result = Flowchart.find_field_from_ast(code_ast, 'no.such.path')
        self.assertEqual(result.body, [])

    def test_detect_decode_utf8(self):
        """detect_decode() must correctly decode plain UTF-8 bytes."""
        from pyflowchart.__main__ import detect_decode
        src = 'print("héllo")'
        result = detect_decode(src.encode('utf-8'))
        self.assertEqual(result, src)

    def test_detect_decode_low_confidence(self):
        """detect_decode() must not crash and must fall back to UTF-8 when
        chardet returns a low or zero confidence score (including when the
        detected encoding is None — the historical TypeError bug).
        """
        from pyflowchart.__main__ import detect_decode
        # Empty bytes: chardet returns encoding=None, confidence=0.0 —
        # previously caused TypeError: '<' not supported between NoneType and float
        result = detect_decode(b'')
        self.assertEqual(result, '')
        # Bytes that chardet is uncertain about should also not crash
        result2 = detect_decode(b'\xff\xfe')
        self.assertIsInstance(result2, str)

    def test_public_api_all_complete(self):
        """__all__ in pyflowchart/__init__.py must expose every public symbol
        and must not leak internal helpers (time, uuid, itertools, List, …).
        """
        import pyflowchart

        # All names declared in __all__ must actually be importable
        for name in pyflowchart.__all__:
            self.assertTrue(
                hasattr(pyflowchart, name),
                msg=f"'{name}' is in __all__ but not importable from pyflowchart",
            )

        # Key public symbols must be present
        required = [
            'Flowchart', 'Node', 'Connection', 'NodesGroup',
            'StartNode', 'EndNode', 'OperationNode', 'InputOutputNode',
            'SubroutineNode', 'ConditionNode', 'TransparentNode', 'CondYN',
            'AstNode', 'FunctionDef', 'Loop', 'If', 'CommonOperation',
            'CallSubroutine', 'BreakContinueSubroutine', 'YieldOutput', 'Return',
            'Match', 'MatchCase', 'Try', 'TryExceptCondition', 'ExceptHandlerCondition',
            'ParseProcessGraph', 'parse', 'output_html',
        ]
        for name in required:
            self.assertIn(name, pyflowchart.__all__, msg=f"'{name}' missing from __all__")

        # Internal names must not be re-exported
        internal = ['time', 'uuid', 'itertools', 'debug', 'AsNode',
                    'TypeVar', 'List', 'Optional', 'Tuple']
        for name in internal:
            self.assertNotIn(name, pyflowchart.__all__, msg=f"internal '{name}' leaked into __all__")

    def test_match_kwargs_forwarded(self):
        """simplify=False must propagate into match-case bodies so that nested
        if-statements are *not* collapsed.  This was broken because parse() was
        called without **kwargs inside MatchCase.parse_body().
        """
        if sys.version_info < (3, 10):
            warnings.warn("match kwargs test requires python >= 3.10")
            return

        code = '''
def fn(a, b):
    match a:
        case 1:
            if b > 0:
                print(b)
'''
        # With simplify=True the inner "if b > 0: print(b)" is collapsed into
        # a single operation node; with simplify=False it stays as a condition
        # node followed by a separate operation node.
        fc_simplified = Flowchart.from_code(code, field='fn', simplify=True).flowchart()
        fc_full = Flowchart.from_code(code, field='fn', simplify=False).flowchart()

        cond_simplified = len(re.findall(r'=>condition:', fc_simplified))
        cond_full = len(re.findall(r'=>condition:', fc_full))

        self.assertGreater(
            cond_full, cond_simplified,
            msg="simplify=False should produce more condition nodes than simplify=True inside match-case bodies",
        )


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
