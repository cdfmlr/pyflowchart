"""
This file manage to translate AST into our Nodes Graph,
By defining AstNodes, and statements to parse AST.

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""

import _ast
import typing
import warnings
from typing import Tuple

from pyflowchart.node import *

# import astunparse
#
# `astunparse` is a third-party package, that provides a function `unparse` to translate AST into Python source code.
# This function is included in Python 3.9 std lib as `ast.unparse`.
# And there are bugs to continue to use `astunparse` in Python 3.9+.
# So here: we use `astunparse` in Python 3.8- and `ast.unparse` in Python 3.9+.
#
# See also:
#  - https://github.com/cdfmlr/pyflowchart/issues/28
#  - https://github.com/simonpercivall/astunparse/issues/56#issuecomment-1438353347
#  - https://docs.python.org/3/library/ast.html#ast.unparse
import sys

if sys.version_info < (3, 9):
    import astunparse
else:
    import ast as astunparse


# TODO: beautify tail connection direction
# TODO: Nested Function

class AstNode(Node):
    """AstNode is nodes from AST
    """

    def __init__(self, ast_object: _ast.AST, **kwargs):
        Node.__init__(self)
        self.ast_object = ast_object

    def ast_to_source(self) -> str:
        """
        self.ast_object (_ast.AST) back to Python source code
        """
        return astunparse.unparse(self.ast_object).strip()


class AstConditionNode(AstNode, ConditionNode):
    """
    AstConditionNode is a ConditionNode for _ast.For | _ast.While | _ast.If ({for|while|if}-sentence in code)
    """

    def __init__(self, ast_cond: _ast.stmt, **kwargs):
        """
        Args:
            ast_cond: instance of _ast.For or _ast.While or _ast.If
            **kwargs: None
        """
        AstNode.__init__(self, ast_cond, **kwargs)
        ConditionNode.__init__(self, cond=self.cond_expr())

    def cond_expr(self) -> str:
        """
        cond_expr returns the condition expression of if|while|for sentence.
        """
        # XXX: the extra cost is too big
        source = astunparse.unparse(self.ast_object)
        loop_statement = source.strip()
        lines = loop_statement.splitlines()
        if len(lines) >= 1:
            return lines[0].rstrip(':')
        else:
            return 'True'

    def fc_connection(self) -> str:
        """
        to avoid meaningless `cond999->`

        Returns: a blank str ""
        """
        return ""


###################
#   FunctionDef   #
###################

class FunctionDefStart(AstNode, StartNode):
    """
    FunctionDefStart is a StartNode from _ast.FunctionDef,
    standing for the start of a function.
    """

    def __init__(self, ast_function_def: _ast.FunctionDef, **kwargs):
        AstNode.__init__(self, ast_function_def, **kwargs)
        StartNode.__init__(self, ast_function_def.name)


class FunctionDefEnd(AstNode, EndNode):
    """
    FunctionDefEnd is a EndNode from _ast.FunctionDef,
     standing for the end of a function.
    """

    def __init__(self, ast_function_def: _ast.FunctionDef, **kwargs):
        AstNode.__init__(self, ast_function_def, **kwargs)
        EndNode.__init__(self, ast_function_def.name)


class FunctionDefArgsInput(AstNode, InputOutputNode):
    """
    FunctionDefArgsInput is a InputOutputNode from _ast.FunctionDef,
    standing for the args (input) of a function.
    """

    def __init__(self, ast_function_def: _ast.FunctionDef, **kwargs):
        AstNode.__init__(self, ast_function_def, **kwargs)
        InputOutputNode.__init__(self, InputOutputNode.INPUT, self.func_args_str())

    def func_args_str(self):
        # TODO(important): handle defaults, vararg, kwonlyargs, kw_defaults, kwarg
        assert isinstance(self.ast_object, _ast.FunctionDef) or \
               hasattr(self.ast_object, "args")
        args = []
        for arg in self.ast_object.args.args:
            args.append(str(arg.arg))

        return ', '.join(args)


class FunctionDef(NodesGroup, AstNode):
    """
    FunctionDef is a AstNode for _ast.FunctionDef (def-sentence in python)

    This class is a NodesGroup with FunctionDefStart & FunctionDefArgsInput & function-body & FunctionDefEnd.
    """

    def __init__(self, ast_func: _ast.FunctionDef, **kwargs):  # _ast.For | _ast.While
        """
        FunctionDef.__init__ makes a NodesGroup object with following Nodes chain:
            FunctionDef -> FunctionDefStart -> FunctionDefArgsInput -> [function-body] -> FunctionDefEnd

        Args:
            **kwargs: None
        """
        AstNode.__init__(self, ast_func, **kwargs)

        # get nodes
        self.func_start = FunctionDefStart(ast_func, **kwargs)
        self.func_args_input = FunctionDefArgsInput(ast_func, **kwargs)
        self.body_head, self.body_tails = self.parse_func_body(**kwargs)
        self.func_end = FunctionDefEnd(ast_func, **kwargs)

        # connect
        self.func_start.connect(self.func_args_input)
        self.func_args_input.connect(self.body_head)
        for t in self.body_tails:
            if isinstance(t, Node):
                t.connect(self.func_end)

        NodesGroup.__init__(self, self.func_start, [self.func_end])

    def parse_func_body(self, **kwargs) -> Tuple[Node, List[Node]]:
        """
        parse function body.

        Returns:
            (Node, List[Node])
            - body_head
            - body_tails
        """
        assert isinstance(self.ast_object, _ast.FunctionDef) or \
               hasattr(self.ast_object, "body")
        p = parse(self.ast_object.body, **kwargs)
        return p.head, p.tails


###################
#   For, while    #
###################

class LoopCondition(AstConditionNode):
    """a AstConditionNode special for Loop"""

    def connect(self, sub_node, direction='') -> None:
        if direction:
            self.set_connect_direction(direction)
        self.connect_no(sub_node)

    def is_one_line_body(self) -> bool:
        """
        Is condition with one line body:
            for|while expr:
                one_line_body
        Returns:
            True or False
        """
        one_line_body = False
        try:
            if not self.connection_yes or not isinstance(self.connection_yes, Connection):
                return False
            loop_body = self.connection_yes.next_node
            one_line_body = isinstance(loop_body, CondYN) and \
                            isinstance(loop_body.sub, Node) and \
                            not isinstance(loop_body.sub, NodesGroup) and \
                            not isinstance(loop_body.sub, ConditionNode) and \
                            len(loop_body.sub.connections) == 1 and \
                            loop_body.sub.connections[0].next_node == self
        except Exception as e:
            print(e)
        return one_line_body


class Loop(NodesGroup, AstNode):
    """
    Loop is a AstNode for _ast.For | _ast.While ({for|while}-sentence in python source code)

    This class is a NodesGroup that connects to LoopCondition & loop-body.
    """

    def __init__(self, ast_loop: _ast.stmt, **kwargs):  # _ast.For | _ast.While
        """
        Construct Loop object will make following Node chain:
            Loop -> LoopCondition -> (yes) -> LoopCondition
                                  -> (no)  -> <next_node>

        Args:
            **kwargs:

                simplify={True | False}: simplify the one_line_body case?
                                           (Default: True)
                                           See `self.simplify`
        """
        AstNode.__init__(self, ast_loop, **kwargs)

        self.cond_node = LoopCondition(ast_loop)

        NodesGroup.__init__(self, self.cond_node)

        self.parse_loop_body(**kwargs)

        self._virtual_no_tail()

        if kwargs.get("simplify", True):
            self.simplify()

    def parse_loop_body(self, **kwargs) -> None:
        """
        Parse and Connect loop-body (a node graph) to self.cond_node (LoopCondition), extend `self.tails` with tails got.
        """
        assert isinstance(self.ast_object, _ast.For) or \
               isinstance(self.ast_object, _ast.While) or \
               hasattr(self.ast_object, "body")

        progress = parse(self.ast_object.body, **kwargs)

        if progress.head is not None:
            process = parse(self.ast_object.body, **kwargs)
            # head
            self.cond_node.connect_yes(process.head)
            # tails connect back to cond
            for tail in process.tails:
                if isinstance(tail, Node):
                    tail.set_connect_direction("left")
                    tail.connect(self.cond_node)
        else:
            noop = SubroutineNode("no-op")
            noop.set_connect_direction("left")
            noop.connect(self.cond_node)
            self.cond_node.connect_yes(noop)

    def _virtual_no_tail(self) -> None:
        # virtual_no = NopNode(parent=self.cond_node)
        # virtual_no = CondYN(self, CondYN.NO)
        virtual_no = None
        self.cond_node.connect_no(virtual_no)

        self.append_tails(self.cond_node.connection_no.next_node)
        pass

    # def connect(self, sub_node) -> None:
    #     self.cond_node.connect_no(sub_node)

    def simplify(self) -> None:
        """
        simplify following case:
            for|while expr:
                one_line_body
        before:
            ... -> Loop (self, NodesGroup) -> LoopCondition('for|while expr') -> CommonOperation('one_line_body') -> ...
        after:
            ... -> Loop (self, NodesGroup) -> CommonOperation('one_line_body while expr') -> ...
        Returns:
            None
        """
        try:
            if self.cond_node.is_one_line_body():  # simplify
                cond = self.cond_node
                assert isinstance(self.cond_node.connection_yes.next_node, CondYN)
                body = self.cond_node.connection_yes.next_node.sub

                simplified = OperationNode(f'{body.node_text} while {cond.node_text.lstrip("for").lstrip("while")}')

                simplified.node_name = self.head.node_name
                self.head = simplified
                self.tails = [simplified]

        except AttributeError as e:
            print(e)


##########
#   If   #
##########

class IfCondition(AstConditionNode):
    """a AstConditionNode special for If"""

    def is_one_line_body(self) -> bool:
        """
        Is IfCondition with one-line body?
            if expr:
                one_line_body

        Returns:
            True or False
        """
        one_line_body = False
        try:
            conn_yes = self.connection_yes
            one_line_body = isinstance(conn_yes, Connection) and \
                            isinstance(conn_yes.next_node, CondYN) and \
                            isinstance(conn_yes.next_node.sub, Node) and \
                            not isinstance(conn_yes.next_node.sub, NodesGroup) and \
                            not isinstance(conn_yes.next_node.sub, ConditionNode) and \
                            not conn_yes.next_node.sub.connections
        except Exception as e:
            print(e)
        return one_line_body

    def is_no_else(self) -> bool:
        """
        Is IfCondition without else-body?
            if expr:
                if-body
            # no elif, no else

        Returns:
            True or False
        """
        no_else = False
        try:
            conn2no = self.connection_no
            no_else = isinstance(conn2no, Connection) and \
                      isinstance(conn2no.next_node, CondYN) and \
                      not conn2no.next_node.sub
        except Exception as e:
            print(e)
        return no_else


class If(NodesGroup, AstNode):
    """
    If is a AstNode for _ast.If (the `if` sentences in python source code)

    This class is a NodesGroup that connects to IfCondition & if-body & else-body.
    """

    def __init__(self, ast_if: _ast.If, **kwargs):
        """
        Construct If object will make following Node chain:
            If -> IfCondition -> (yes) -> yes-path
                              -> (no)  -> no-path

        Args:
            **kwargs:

                simplify={True | False}: simplify the one_line_body case?
                                           (Default: True)
                                           See `self.simplify`
        """
        AstNode.__init__(self, ast_if, **kwargs)

        self.cond_node = IfCondition(ast_if)

        NodesGroup.__init__(self, self.cond_node)

        self.parse_if_body(**kwargs)
        self.parse_else_body(**kwargs)

        if kwargs.get("simplify", True):
            self.simplify()
        if kwargs.get("conds_align", False) and self.cond_node.is_no_else():
            self.cond_node.connection_yes.set_param("right")

    def parse_if_body(self, **kwargs) -> None:
        """
        Parse and Connect if-body (a node graph) to self.cond_node (IfCondition).
        """
        assert isinstance(self.ast_object, _ast.If) or \
               hasattr(self.ast_object, "body")

        progress = parse(self.ast_object.body, **kwargs)

        if progress.head is not None:
            self.cond_node.connect_yes(progress.head)
            # for t in progress.tails:
            #     if isinstance(t, Node):
            #         t.set_connect_direction("right")
            self.extend_tails(progress.tails)
        else:  # connect virtual connection_yes
            # virtual_yes = NopNode(parent=self.cond_node)
            # virtual_yes = CondYN(self, CondYN.YES)
            virtual_yes = None
            self.cond_node.connect_yes(virtual_yes)

            self.append_tails(self.cond_node.connection_yes.next_node)

    def parse_else_body(self, **kwargs) -> None:
        """
        Parse and Connect else-body (a node graph) to self.cond_node (IfCondition).
        """
        assert isinstance(self.ast_object, _ast.If) or \
               hasattr(self.ast_object, "orelse")

        progress = parse(self.ast_object.orelse, **kwargs)

        if progress.head is not None:
            self.cond_node.connect_no(progress.head)
            self.extend_tails(progress.tails)
        else:  # connect virtual connection_no
            # virtual_no = NopNode(parent=self.cond_node)
            # virtual_no = CondYN(self, CondYN.NO)
            virtual_no = None
            self.cond_node.connect_no(virtual_no)

            self.append_tails(self.cond_node.connection_no.next_node)

    def simplify(self) -> None:
        """simplify the one-line body case:
            if expr:
                one_line_body
            # no else

        before:
            ... -> If (self, NodesGroup) -> IfCondition('if expr') -> CommonOperation('one_line_body') -> ...
        after:
            ... -> If (self, NodesGroup) -> CommonOperation('one_line_body if expr') -> ...
        Returns:
            None
        """
        try:
            if self.cond_node.is_no_else() and self.cond_node.is_one_line_body():  # simplify
                cond = self.cond_node
                if not cond.connection_yes:
                    return

                assert isinstance(self.cond_node.connection_yes.next_node, CondYN)
                body = self.cond_node.connection_yes.next_node.sub

                simplified = OperationNode(f'{body.node_text} if {cond.node_text.lstrip("if")}')

                simplified.node_name = self.head.node_name
                self.head = simplified
                self.tails = [simplified]

        except AttributeError as e:
            print(e)

    def align(self):
        """ConditionNode alignment support #14
            if cond1:
                op1
            if cond2:
                op2
            if cond3:
                op3
            op_end

        Simplify: add param `align-next=no` to cond1~3, which improves the generated flowchart.

        See:
            - https://github.com/cdfmlr/pyflowchart/issues/14
            - https://github.com/adrai/flowchart.js/issues/221#issuecomment-846919013
            - https://github.com/adrai/flowchart.js/issues/115
        """
        self.cond_node.no_align_next()


####################
#   Common, Call   #
####################

class CommonOperation(AstNode, OperationNode):
    """
    CommonOperation is an OperationNode for any _ast.AST (any sentence in python source code)
    """

    def __init__(self, ast_object: _ast.AST, **kwargs):
        AstNode.__init__(self, ast_object, **kwargs)
        OperationNode.__init__(self, operation=self.ast_to_source())


class CallSubroutine(AstNode, SubroutineNode):
    """
    CallSubroutine is an SubroutineNode for _ast.Call (function call sentence in source)
    """

    def __init__(self, ast_call: _ast.Call, **kwargs):
        AstNode.__init__(self, ast_call, **kwargs)
        SubroutineNode.__init__(self, self.ast_to_source())


##############################
#   Break, Continue, Yield   #
##############################


class BreakContinueSubroutine(AstNode, SubroutineNode):
    """
    BreakContinueSubroutine is an SubroutineNode for _ast.Break or _ast.Continue (break/continue sentence in source)
    """

    # TODO: Including information about the LoopCondition that is to be break/continue.

    def __init__(self, ast_break_continue: _ast.stmt, **kwargs):  # Break & Continue is subclass of stmt
        AstNode.__init__(self, ast_break_continue, **kwargs)
        SubroutineNode.__init__(self, self.ast_to_source())

    def connect(self, sub_node, direction='') -> None:
        # a BreakContinueSubroutine should connect to nothing
        pass


class YieldOutput(AstNode, InputOutputNode):
    """
     YieldOutput is a InputOutputNode (Output) for _ast.Yield (yield sentence in python source code)
    """

    def __init__(self, ast_return: _ast.Return, **kwargs):
        AstNode.__init__(self, ast_return, **kwargs)
        InputOutputNode.__init__(self, InputOutputNode.OUTPUT, self.ast_to_source())


##############
#   Return   #
##############

class ReturnOutput(AstNode, InputOutputNode):
    """
     ReturnOutput is a InputOutputNode (Output) for _ast.Return (return sentence in python source code)
    """

    def __init__(self, ast_return: _ast.Return, **kwargs):
        AstNode.__init__(self, ast_return, **kwargs)
        InputOutputNode.__init__(self, InputOutputNode.OUTPUT, self.ast_to_source().lstrip("return"))


class ReturnEnd(AstNode, EndNode):
    """
    ReturnEnd is a EndNode for _ast.Return (return sentence in python source code)
    """

    def __init__(self, ast_return: _ast.Return, **kwargs):
        AstNode.__init__(self, ast_return, **kwargs)
        EndNode.__init__(self, "function return")  # TODO: the returning function name


class Return(NodesGroup, AstNode):
    """
    ReturnEnd is a AstNode for _ast.Return (return sentence in python source code)

    This class is an invisible virtual Node (i.e. NodesGroup) that connects to ReturnOutput & ReturnEnd.
    """

    def __init__(self, ast_return: _ast.Return, **kwargs):
        """
        Construct Return object will make following Node chain:
            Return -> ReturnOutput -> ReturnEnd
        Giving return sentence without return-values, the ReturnOutput will be omitted: (Return -> ReturnEnd)

        Args:
            **kwargs: None
        """
        AstNode.__init__(self, ast_return, **kwargs)

        self.output_node = None
        self.end_node = None

        self.head = None

        self.end_node = ReturnEnd(ast_return, **kwargs)
        self.head = self.end_node
        if ast_return.value:
            self.output_node = ReturnOutput(ast_return, **kwargs)
            self.output_node.connect(self.end_node)
            self.head = self.output_node

        self.connections.append(Connection(self.head))

        NodesGroup.__init__(self, self.head, [self.end_node])

    # def fc_definition(self) -> str:
    #     """
    #     Return object is invisible
    #     """
    #     return NodesGroup.fc_definition(self)
    #
    # def fc_connection(self) -> str:
    #     """
    #     Return object is invisible
    #     """
    #     return NodesGroup.fc_connection(self)
    #
    def connect(self, sub_node, direction='') -> None:
        """
        Return should not be connected with anything
        """
        pass


#############
#   Match   #
#############

# _ast_Match_t is a type alias to _ast.Match in Python 3.10+.
# for old Python versions, it can be anything (_ast.AST).
#
# This is a workaround for the problem that
# an _ast.NON_EXIST as a type hint will prevent the whole program from running:
#     AttributeError: module '_ast' has no attribute 'Match'
_ast_Match_t = _ast.AST
if sys.version_info >= (3, 10):
    _ast_Match_t = _ast.Match

# similar to _ast_Match_t
_ast_match_case_t = _ast.AST
if sys.version_info >= (3, 10):
    _ast_match_case_t = _ast.match_case


class MatchCaseCondition(ConditionNode):
    """
    MatchCaseConditionNode is ConditionNode special for the condition of a case in match-case:

        match {subject}:
            case {pattern} if {guard}:
                ...
    """

    def __init__(self, ast_match_case: _ast_match_case_t, subject: _ast.AST, **kwargs):
        """
        Args:
            ast_match_case: instance of _ast.match_case
            **kwargs: None
        """
        ConditionNode.__init__(self, cond=self.cond_expr(ast_match_case, subject))

    @staticmethod
    def cond_expr(ast_match_case: _ast_match_case_t, subject: _ast.AST) -> str:
        """
        cond_expr returns the condition expression of match-case sentence.

            "if {subject} match case {pattern} [if {guard}]"
        """
        subject = astunparse.unparse(subject).strip()
        pattern = astunparse.unparse(ast_match_case.pattern).strip()
        guard = astunparse.unparse(ast_match_case.guard).strip() if ast_match_case.guard else None

        s = f"if {subject} match case {pattern}"
        if guard:
            s += f" if {guard}"

        return s


class MatchCase(NodesGroup, AstNode):
    """
    MatchCase is a NodesGroup that connects to MatchCaseConditionNode & case-body.
    It is from a case in match-case:
        match {subject}:
            case {pattern} if {guard}:
                {body}
    We parse it to an NodesGroup, that looks like an If without Else:
        If (self, NodesGroup)
            -> IfCondition('if {subject} match case {pattern} [if {guard}]') ->
                -> yes -> [body]
                -> no -> aTransparentNode
    """

    def __init__(self, ast_match_case: _ast_match_case_t, subject: _ast.AST, **kwargs):
        AstNode.__init__(self, ast_match_case, **kwargs)

        self.cond_node = MatchCaseCondition(ast_match_case, subject)

        NodesGroup.__init__(self, self.cond_node)

        self.parse_body(**kwargs)

    def parse_body(self, **kwargs) -> None:
        assert isinstance(self.ast_object, _ast.match_case) or \
               hasattr(self.ast_object, "body")

        progress = parse(self.ast_object.body)

        if progress.head is not None:
            self.cond_node.connect_yes(progress.head)
            self.extend_tails(progress.tails)

        # always connect a transparent node as the no-path
        virtual_tail = TransparentNode(self.cond_node, connect_params=["no"])
        self.cond_node.connect_no(virtual_tail)
        self.append_tails(virtual_tail)

    def inlineable(self):
        """
        Is this MatchCase inlineable?
        If so, we can inline it into the MatchCondition.
        """
        conn_yes = self.cond_node.connection_yes
        try:
            one_line_body = isinstance(conn_yes, Connection) and \
                            isinstance(conn_yes.next_node, CondYN) and \
                            isinstance(conn_yes.next_node.sub, Node) and \
                            not isinstance(conn_yes.next_node.sub, NodesGroup) and \
                            not isinstance(conn_yes.next_node.sub, ConditionNode) and \
                            not conn_yes.next_node.sub.connections
        except Exception:
            # print(e)
            one_line_body = False
        return one_line_body

    def simplify(self) -> None:
        warnings.warn("MatchCase.simplify() is buggy, use it with caution.")

        if not self.inlineable():
            return

        try:
            conn_yes = self.cond_node.connection_yes

            assert isinstance(conn_yes, Connection)
            assert isinstance(conn_yes.next_node, CondYN)
            assert isinstance(conn_yes.next_node.sub, Node)

            body = conn_yes.next_node.sub

            simplified = OperationNode(f'{body.node_text} {self.cond_node.node_text}')

            simplified.node_name = self.head.node_name + "inline"
            self.head = simplified
            self.tails = [simplified]

        except AttributeError as e:
            warnings.warn(f"MatchCase.simplify() failed: {e}")
        except AssertionError as e:
            warnings.warn(f"MatchCase.simplify() failed: {e}")


class Match(NodesGroup, AstNode):
    """
    Match is a AstNode for _ast.Match (the `match-case` sentences in python source code)

    This class is a NodesGroup that connects to MatchCondition & its cases.
    """

    def __init__(self, ast_match: _ast_Match_t, **kwargs):
        """
        Construct Match object will make following Node chain:
            Match -> MatchCondition -> (case1) -> case1-path
                                    -> (case2) -> case2-path
                                    ...

        A match-case sentence contains:

            match {subject}:
                case {pattern} if {guard}:
                    {body}
                case ...:
                    ...

        Args:
            **kwargs:

                simplify={True | False}: simplify the one_line_body case?
                                           (Default: True)
                                           See `self.simplify`
        """
        AstNode.__init__(self, ast_match, **kwargs)

        # A Cond for match_case should be represented as "if {subject} match case {pattern}"
        self.subject = ast_match.subject

        # self.head = TransparentNode(self)
        # fuck the multi inheritance,,, my brain is buffer overflowing
        # god bless the jetbrains helped me figure out this overstep
        # well, never mind. I believe that NodesGroup.__init__()
        # is the right way to set it up as well as self.head properly.

        # Each case is a condition node.
        # Since we have not parsed any case body, (nor I want to peek one),
        # here we use a transparent node as the head of the NodesGroup.
        transparent_head = TransparentNode(self)
        NodesGroup.__init__(self, transparent_head)
        assert self.head is transparent_head

        self.cases: List[MatchCase] = []
        self.parse_cases(**kwargs)

        # remove the transparent_head
        try:
            debug(f"Match.__init__() replace head: self.head before: {type(self.head)}: {self.head.__dict__}")
            self.head = self.head.connections[0].next_node
            debug(f"Match.__init__() replace head self.head after: {type(self.head)}: {self.head.__dict__}")
        except IndexError or AttributeError:
            self.head = CommonOperation(ast_match)
            self.tails = [self.head]

        # simplify works not well, so I disable it by default.
        # (it's still possible to call simplify manually, though)
        # if kwargs.get("simplify", True):
        #     self.simplify()

    def parse_cases(self, **kwargs) -> None:
        """
        Parse and Connect cases of the match
        """
        assert isinstance(self.ast_object, _ast.Match) or \
               hasattr(self.ast_object, "cases")

        last_case = self.head  # at first, it's a transparent node
        for match_case in self.ast_object.cases:
            match_case_node = MatchCase(match_case, self.subject, **kwargs)
            last_case.connect(match_case_node)
            last_case = match_case_node
            self.cases.append(match_case_node)

        # connect the last case to the end of the match
        try:
            self.tails.extend(last_case.tails)
        except AttributeError:
            self.tails.append(last_case)

        # if kwargs.get("simplify", True):
        #     self.simplify()

    def simplify(self) -> None:
        """
        simplify the inlineable (one-line body) cases:
            match {subject}:
                case {pattern} if {guard}:
                    one_line_body
        """
        warnings.warn("Match.simplify() is buggy, use it with caution.")

        try:
            for case_node in self.cases:
                if case_node.inlineable():
                    case_node.simplify()
        except AttributeError as e:
            warnings.warn(f"Match.simplify() failed: {e}")


# With Python < 3.10, We have no _ast.Match and _ast.match_case,
# unable to parse match-case sentence. Just trait it as a common sentence.
# That is, unparse the whole match-case sentence, put the result into a OperationNode.
#
# DUCK, with Python 3.7, it is not possible for ast to parse match-case sentence:
#     File "/Users/z/Projects/pyflowchart/pyflowchart/flowchart.py", line 94, in from_code
#       code_ast = ast.parse(code)
#     File "/Users/z/.pyenv/versions/3.7.17/lib/python3.7/ast.py", line 35, in parse
#       return compile(source, filename, mode, PyCF_ONLY_AST)
#     File "<unknown>", line 3
#       match b:
#         ^
#     SyntaxError: invalid syntax
# So, this is in vain.
if sys.version_info < (3, 10):
    Match = CommonOperation

# Sentence: common | func | cond | loop | ctrl
# - func: def
# - cond: if
# - loop: for, while
# - ctrl: break, continue, return, yield, call
# - common: others
# Special sentence: cond | loop | ctrl
# TODO: Try, With

__func_stmts = {
    _ast.FunctionDef: FunctionDef
}

__cond_stmts = {
    _ast.If: If,
    # _ast_Match_t: Match,  # need to check Python version, handle it later manually.
}

__loop_stmts = {
    _ast.For: Loop,
    _ast.While: Loop,
}

__ctrl_stmts = {
    _ast.Break: BreakContinueSubroutine,
    _ast.Continue: BreakContinueSubroutine,
    _ast.Return: Return,
    _ast.Yield: YieldOutput,
    _ast.Call: CallSubroutine,
}

# merge dict: PEP448
__special_stmts = {**__func_stmts, **__cond_stmts, **__loop_stmts, **__ctrl_stmts}


class ParseProcessGraph(NodesGroup):
    """
    ParseGraph is a NodesGroup for parse process result.
    """
    pass


def parse(ast_list: List[_ast.AST], **kwargs) -> ParseProcessGraph:
    """
    parse an ast_list (from _ast.Module/FunctionDef/For/If/etc.body)

    Args:
        ast_list: a list of _ast.AST object

    Keyword Args:
        * simplify: for If & Loop: simplify the one line body cases
        * conds_align: for If: allow the align-next option set for the condition nodes.
            See https://github.com/cdfmlr/pyflowchart/issues/14

    Returns:
        ParseGraph
    """
    head_node = None
    tail_node = None

    process = ParseProcessGraph(head_node, tail_node)

    for ast_object in ast_list:
        # ast_node_class: some special AstNode subclass or CommonOperation by default.
        ast_node_class = __special_stmts.get(type(ast_object), CommonOperation)

        # special case:  Match for Python 3.10+
        if sys.version_info >= (3, 10) and type(ast_object) == _ast_Match_t:
            ast_node_class = Match

        # special case: special stmt as a expr value. e.g. function call
        if type(ast_object) == _ast.Expr:
            if hasattr(ast_object, "value"):
                ast_node_class = __special_stmts.get(type(ast_object.value), CommonOperation)
            else:  # ast_object has no value attribute
                ast_node_class = CommonOperation

        assert issubclass(ast_node_class, AstNode)

        node = ast_node_class(ast_object, **kwargs)

        if head_node is None:  # is the first node
            head_node = node
            tail_node = node
        else:
            tail_node.connect(node)

            # ConditionNode alignment support (Issue#14)
            # XXX: It's ugly to handle it here. But I have no idea, for this moment, to make it ELEGANT.
            if isinstance(tail_node, If) and isinstance(node, If) and \
                    kwargs.get("conds_align", False):
                tail_node.align()

            tail_node = node

    process.set_head(head_node)
    process.append_tails(tail_node)

    return process
