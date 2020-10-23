"""
This file manage to translate AST into our Nodes Graph,
By defining AstNodes, and statements to parse AST.

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""

import _ast
from typing import List

import astunparse

from pyflowchart.node import *


# TODO: beautify tail connection direction
# TODO: Nested Function

class AstNode(Node):
    """AstNode is nodes from AST
    """

    def __init__(self, ast_object: _ast.AST):
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

    def __init__(self, ast_cond: _ast.stmt):
        """
        Args:
            ast_cond: instance of _ast.For or _ast.While or _ast.If
        """
        AstNode.__init__(self, ast_cond)
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

    def __init__(self, ast_function_def: _ast.FunctionDef):
        AstNode.__init__(self, ast_function_def)
        StartNode.__init__(self, ast_function_def.name)


class FunctionDefEnd(AstNode, EndNode):
    """
    FunctionDefEnd is a EndNode from _ast.FunctionDef,
     standing for the end of a function.
    """

    def __init__(self, ast_function_def: _ast.FunctionDef):
        AstNode.__init__(self, ast_function_def)
        EndNode.__init__(self, ast_function_def.name)


class FunctionDefArgsInput(AstNode, InputOutputNode):
    """
    FunctionDefArgsInput is a InputOutputNode from _ast.FunctionDef,
    standing for the args (input) of a function.
    """

    def __init__(self, ast_function_def: _ast.FunctionDef):
        AstNode.__init__(self, ast_function_def)
        InputOutputNode.__init__(self, InputOutputNode.INPUT, self.func_args_str())

    def func_args_str(self):
        # TODO(important): handle defaults, vararg, kwonlyargs, kw_defaults, kwarg
        args = []
        for arg in self.ast_object.args.args:
            args.append(str(arg.arg))

        return ', '.join(args)


class FunctionDef(NodesGroup, AstNode):
    """
    FunctionDef is a AstNode for _ast.FunctionDef (def-sentence in python)

    This class is a NodesGroup with FunctionDefStart & FunctionDefArgsInput & function-body & FunctionDefEnd.
    """

    def __init__(self, ast_func: _ast.FunctionDef):  # _ast.For | _ast.While
        """
        FunctionDef.__init__ makes a NodesGroup object with following Nodes chain:
            FunctionDef -> FunctionDefStart -> FunctionDefArgsInput -> [function-body] -> FunctionDefEnd
        """
        AstNode.__init__(self, ast_func)

        # get nodes
        self.func_start = FunctionDefStart(ast_func)
        self.func_args_input = FunctionDefArgsInput(ast_func)
        self.body_head, self.body_tails = self.parse_func_body()
        self.func_end = FunctionDefEnd(ast_func)

        # connect
        self.func_start.connect(self.func_args_input)
        self.func_args_input.connect(self.body_head)
        for t in self.body_tails:
            if isinstance(t, Node):
                t.connect(self.func_end)

        NodesGroup.__init__(self, self.func_start, [self.func_end])

    def parse_func_body(self) -> (Node, List[Node]):
        """
        parse function body.

        Returns:
            (Node, List[Node])
            - body_head
            - body_tails
        """
        p = parse(self.ast_object.body)
        return p.head, p.tails


###################
#   For, while    #
###################

class LoopCondition(AstConditionNode):
    """a AstConditionNode special for Loop"""

    def connect(self, sub_node) -> None:
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
            loop_body = self.connection_yes
            one_line_body = isinstance(loop_body, CondYN) and \
                            isinstance(loop_body.sub, Node) and \
                            not isinstance(loop_body.sub, NodesGroup) and \
                            not isinstance(loop_body.sub, ConditionNode) and \
                            len(loop_body.sub.connections) == 1 and \
                            loop_body.sub.connections[0] == self
        except Exception as e:
            print(e)
        return one_line_body


class Loop(NodesGroup, AstNode):
    """
    Loop is a AstNode for _ast.For | _ast.While ({for|while}-sentence in python source code)

    This class is a NodesGroup that connects to LoopCondition & loop-body.
    """

    def __init__(self, ast_loop: _ast.stmt):  # _ast.For | _ast.While
        """
        Construct Loop object will make following Node chain:
            Loop -> LoopCondition -> (yes) -> LoopCondition
                                  -> (no)  -> <next_node>
        """
        AstNode.__init__(self, ast_loop)

        self.cond_node = LoopCondition(ast_loop)

        NodesGroup.__init__(self, self.cond_node)

        self.parse_loop_body()

        self._virtual_no_tail()

        self.simplify()

    def parse_loop_body(self) -> None:
        """
        Parse and Connect loop-body (a node graph) to self.cond_node (LoopCondition), extend self.tails with tails got.
        """
        progress = parse(self.ast_object.body)

        if progress.head is not None:
            process = parse(self.ast_object.body)
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
            self.cond_node.connection_yes(noop)

    def _virtual_no_tail(self) -> None:
        virtual_no = CondYN(self, CondYN.NO)

        self.cond_node.connection_no = virtual_no
        self.cond_node.connections.append(virtual_no)

        self.append_tails(virtual_no)

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
                body = self.cond_node.connection_yes.sub

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
            yes = self.connection_yes
            one_line_body = isinstance(yes, CondYN) and \
                            isinstance(yes.sub, Node) and \
                            not isinstance(yes.sub, NodesGroup) and \
                            not isinstance(yes.sub, ConditionNode) and \
                            not yes.sub.connections
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
            no = self.connection_no
            no_else = isinstance(no, CondYN) and \
                      not no.sub
        except Exception as e:
            print(e)
        return no_else


class If(NodesGroup, AstNode):
    """
    If is a AstNode for _ast.If (the if sentences in python source code)

    This class is a NodesGroup that connects to IfCondition & if-body & else-body.
    """

    def __init__(self, ast_if: _ast.If):
        """
        Construct If object will make following Node chain:
            If -> IfCondition -> (yes) -> yes-path
                              -> (no)  -> no-path
        """
        AstNode.__init__(self, ast_if)

        self.cond_node = IfCondition(ast_if)

        NodesGroup.__init__(self, self.cond_node)

        self.parse_if_body()
        self.parse_else_body()

        # TODO: let use choice simplify or not
        self.simplify()

    def parse_if_body(self) -> None:
        """
        Parse and Connect if-body (a node graph) to self.cond_node (IfCondition).
        """
        progress = parse(self.ast_object.body)

        if progress.head is not None:
            self.cond_node.connect_yes(progress.head)
            # for t in progress.tails:
            #     if isinstance(t, Node):
            #         t.set_connect_direction("right")
            self.extend_tails(progress.tails)
        else:  # connect virtual connection_yes
            virtual_yes = CondYN(self, CondYN.YES)
            self.cond_node.connection_yes = virtual_yes
            self.cond_node.connections.append(virtual_yes)

            self.append_tails(virtual_yes)

    def parse_else_body(self) -> None:
        """
        Parse and Connect else-body (a node graph) to self.cond_node (IfCondition).
        """
        progress = parse(self.ast_object.orelse)

        if progress.head is not None:
            self.cond_node.connect_no(progress.head)
            self.extend_tails(progress.tails)
        else:  # connect virtual connection_no
            virtual_no = CondYN(self, CondYN.NO)
            self.cond_node.connection_no = virtual_no
            self.cond_node.connections.append(virtual_no)

            self.append_tails(virtual_no)

    def simplify(self) -> None:
        """
        simplify following case:
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
                body = self.cond_node.connection_yes.sub

                simplified = OperationNode(f'{body.node_text} if {cond.node_text.lstrip("if")}')

                simplified.node_name = self.head.node_name
                self.head = simplified
                self.tails = [simplified]

        except AttributeError as e:
            print(e)


####################
#   Common, Call   #
####################

class CommonOperation(AstNode, OperationNode):
    """
    CommonOperation is an OperationNode for any _ast.AST (any sentence in python source code)
    """

    def __init__(self, ast_object: _ast.AST):
        AstNode.__init__(self, ast_object)
        OperationNode.__init__(self, operation=self.ast_to_source())


class CallSubroutine(AstNode, SubroutineNode):
    """
    CallSubroutine is an SubroutineNode for _ast.Call (function call sentence in source)
    """

    def __init__(self, ast_call: _ast.Call):
        AstNode.__init__(self, ast_call)
        SubroutineNode.__init__(self, self.ast_to_source())


##############################
#   Break, Continue, Yield   #
##############################


class BreakContinueSubroutine(AstNode, SubroutineNode):
    """
    BreakContinueSubroutine is an SubroutineNode for _ast.Break or _ast.Continue (break/continue sentence in source)
    """

    # TODO: Including information about the LoopCondition that is to be break/continue.

    def __init__(self, ast_break_continue: _ast.stmt):  # Break & Continue is subclass of stmt
        AstNode.__init__(self, ast_break_continue)
        SubroutineNode.__init__(self, self.ast_to_source())

    def connect(self, sub_node) -> None:
        # a BreakContinueSubroutine should connect to nothing
        pass


class YieldOutput(AstNode, InputOutputNode):
    """
     YieldOutput is a InputOutputNode (Output) for _ast.Yield (yield sentence in python source code)
    """

    def __init__(self, ast_return: _ast.Return):
        AstNode.__init__(self, ast_return)
        InputOutputNode.__init__(self, InputOutputNode.OUTPUT, self.ast_to_source())


##############
#   Return   #
##############

class ReturnOutput(AstNode, InputOutputNode):
    """
     ReturnOutput is a InputOutputNode (Output) for _ast.Return (return sentence in python source code)
    """

    def __init__(self, ast_return: _ast.Return):
        AstNode.__init__(self, ast_return)
        InputOutputNode.__init__(self, InputOutputNode.OUTPUT, self.ast_to_source().lstrip("return"))


class ReturnEnd(AstNode, EndNode):
    """
    ReturnEnd is a EndNode for _ast.Return (return sentence in python source code)
    """

    def __init__(self, ast_return: _ast.Return):
        AstNode.__init__(self, ast_return)
        EndNode.__init__(self, "function return")  # TODO: the returning function name


class Return(NodesGroup, AstNode):
    """
    ReturnEnd is a AstNode for _ast.Return (return sentence in python source code)

    This class is a invisible virtual Node (i.e. NodesGroup) that connects to ReturnOutput & ReturnEnd.
    """

    def __init__(self, ast_return: _ast.Return):
        """
        Construct Return object will make following Node chain:
            Return -> ReturnOutput -> ReturnEnd
        Giving return sentence without return-values, the ReturnOutput will be omitted: (Return -> ReturnEnd)
        """
        AstNode.__init__(self, ast_return)

        self.output_node = None
        self.end_node = None

        self.head = None

        self.end_node = ReturnEnd(ast_return)
        self.head = self.end_node
        if ast_return.value:
            self.output_node = ReturnOutput(ast_return)
            self.output_node.connect(self.end_node)
            self.head = self.output_node

        self.connections.append(self.head)

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
    def connect(self, sub_node) -> None:
        """
        Return should not be connect with anything
        """
        pass


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


def parse(ast_list: List[_ast.AST]) -> ParseProcessGraph:
    """
    parse a ast_list (from _ast.Module/FunctionDef/For/If/etc.body)

    Args:
        ast_list: a list of _ast.AST object

    Returns:
        ParseGraph
    """
    head_node = None
    tail_node = None

    process = ParseProcessGraph(head_node, tail_node)

    for ast_object in ast_list:
        # ast_node_class: some special AstNode subclass or CommonOperation by default.
        ast_node_class = __special_stmts.get(type(ast_object), CommonOperation)

        # special case: special stmt as a expr value. e.g. function call
        if type(ast_object) == _ast.Expr:
            try:
                ast_node_class = __special_stmts.get(type(ast_object.value), CommonOperation)
            except AttributeError:
                # ast_object has no value attribute
                ast_node_class = CommonOperation

        assert issubclass(ast_node_class, AstNode)

        node = ast_node_class(ast_object)

        if head_node is None:  # is the first node
            head_node = node
            tail_node = node
        else:
            tail_node.connect(node)
            tail_node = node

    process.set_head(head_node)
    process.append_tails(tail_node)

    return process
