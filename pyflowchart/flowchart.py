"""
This file defines Flowchart.

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""

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
         after which join everything together, returns an whole flowchart DSL as string.

        Returns:
            a flowchart.js DSL string including node definitions & connections
        """

        return self.fc_definition() + '\n' + self.fc_connection()

    @staticmethod
    def from_code(code: str):
        """
        Get a Flowchart instance from a str of Python code

        Returns:
            A Flowchart instance parsed from given code.
        """
        code_ast = ast.parse(code)
        p = parse(code_ast.body)
        return Flowchart(p.head)
