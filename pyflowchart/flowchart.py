"""
This file defines Flowchart.

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""
import _ast
import ast

from pyflowchart.ast_node import parse
from pyflowchart.node import Node, NodesGroup


class Flowchart(NodesGroup):
    """
    Flowchart is a no-tails-NodesGroup with a flowchart() method.

    Calls flowchart method of Flowchart instance to get a flowchart.js DSL.
    """

    def __init__(self, head_node: Node):
        """Flowchart is a graph of Node.

        Flowchart(start_node) constructs a Flowchart instance with a head (start) Node
        """
        super().__init__(head_node)

    def flowchart(self) -> str:
        """flowchart returns a full flowchart starting from head Node.

        Recursively get definitions & connections of current Node (self) and
         all of its connections (sub Node) encountered,
         after which join everything together, returns the whole flowchart DSL as string.

        Returns:
            a flowchart.js DSL string including node definitions & connections
        """

        return self.fc_definition() + '\n' + self.fc_connection()

    @staticmethod
    def from_code(code: str, field: str = "", inner=True, simplify=True, conds_align=False):
        """
        Get a Flowchart instance from a str of Python code.

        Args:

            code:  str,  Python code to draw flowchart
            field: str,  path to field (function) you want to draw flowchart
            inner: bool, True: parse the body of field; Field: parse the body as an object
            simplify: bool, for If & Loop statements: simplify the one-line-body or not.
            conds_align: bool, for consecutive If statements: conditionNode alignment support (Issue#14) or not

        Returns:
            A Flowchart instance parsed from given code.

        `inner=True` means parse `field.body`, otherwise parse [field]. E.g.

        ```
        def a():
            print('a')
        ```

        inner=True  => `st (function a) -> subroutine (print) -> end`
        inner=False => `op=>operation: def a(): print('a')`

        The field is the path to the target of flowchartilizing.
        It should be the *path* to a `def` code block in code. E.g.

        ```
        def foo():
            pass

        class Bar():
            def fuzz(self):
                pass
            def buzz(self, f):
                def g(self):
                    f(self)
                return g(self)

        Bar().buzz(foo)
        ```

        Available path:

        - "" (means the whole code)
        - "foo"
        - "Bar.fuzz"
        - "Bar.buzz"
        - "Bar.buzz.g"
        """
        code_ast = ast.parse(code)

        field_ast = Flowchart.find_field_from_ast(code_ast, field)

        assert hasattr(field_ast, "body")
        assert field_ast.body, f"{field}: nothing to parse. Check given code and field please."

        f = field_ast.body if inner else [field_ast]
        p = parse(f, simplify=simplify, conds_align=conds_align)
        return Flowchart(p.head)

    @staticmethod
    def find_field_from_ast(ast_obj: _ast.AST, field: str) -> _ast.AST:
        """Find a field from AST.

        This function finds the given `field` in `ast_obj.body`, return the found AST object
        or an `_ast.AST` object whose body attribute is [].
        Specially, if field="", returns `ast_obj`.

        A field is the *path* to a `def` code block in code (i.e. a `FunctionDef` object in AST). E.g.

        ```
        def foo():
            pass

        class Bar():
            def fuzz(self):
                pass
            def buzz(self, f):
                def g(self):
                    f(self)
                return g(self)

        Bar().buzz(foo)
        ```

        Available path:

        - "" (means the whole ast_obj)
        - "foo"
        - "Bar.fuzz"
        - "Bar.buzz"
        - "Bar.buzz.g"

        Args:
            ast_obj: given AST
            field: path to a `def`

        Returns: an _ast.AST object
        """
        if field == "":
            return ast_obj

        field_list = field.split('.')
        try:
            for fd in field_list:
                for ao in ast_obj.body:  # raises AttributeError: ast_obj along the field path has no body
                    if hasattr(ao, 'name') and ao.name == fd:
                        ast_obj = ao
            assert ast_obj.name == field_list[-1], "field not found"
        except (AttributeError, AssertionError):
            ast_obj.body = []

        return ast_obj
