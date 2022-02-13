"""
This file defines basic class Node, NodesGroup and
a variety of node subclass, one-to-one correspondence
with flowchart.js flowchart DSL Nodes (except parallel).

Copyright 2020 CDFMLR. All rights reserved.
Use of this source code is governed by a MIT
license that can be found in the LICENSE file.
"""

import time
import uuid
import itertools  # for count


# TODO(v1.0): Noticing that all connections look like `xxx(params)->yyy`,
#       where params maybe something like `right`, `yes`, or `yes,right`,
#       A good idea is to make a new class Connection as:
#           class Connection(object):
#               next_node: Node
#               params: dict
#       It helps to customize the directions of connections and we may not even
#       need a CondYN anymore!
#       But this changes a lot and seems not necessary now. So it's maybe a
#       further version 1.0 job to achieve this.

class Node(object):
    """Node is a abstract class for kinds of flowchart node.
    """
    node_type = 'node'  # flowchart.js Node Syntax: nodeType

    # object id: an iterator
    # each entities call next(self._node_id) to get an ID.
    # XXX: I am not fully sure that this is thread-safe.
    _node_id = itertools.count(0)

    def __init__(self):
        self.node_name = ''  # flowchart.js Node Syntax: nodeName
        self.node_text = ''  # flowchart.js Node Syntax: nodeText
        self.connections = []  # list<Node>, connected (next / sub) nodes.

        self.params = {}  # flowchart.js #115 e.g. `element(param1=value1,param2=value2)=>start: Start`
        self.connect_direction = None  # custom thisNode(connect_direction)->nextNode

        self.__visited = None

        self.id = next(self._node_id)

    def fc_definition(self) -> str:
        """fc_definition returns the flowchart.js node definition string of current Node  (self only, subs excepted).
        Returns a flowchart.js node definition string:
            "node_name=>node_type: node_text".
        And if params is not empty, regarding https://github.com/adrai/flowchart.js/issues/115,
        it will output:
            "node_name(param1=value1,param2=value2)=>node_type: node_text"

        Returns:
            str
        """
        params = ''
        if self.params:
            params = ','.join((f'{k}={self.params[k]}' for k in self.params))  # 'param1=value1,param2=value2'
            params = f'({params})'

        return f'{self.node_name}{params}=>{self.node_type}: {self.node_text}\n'

    def fc_connection(self) -> str:
        """fc_connection returns the flowchart.js node connection string of current Node (self only, subs excepted).

        Returns:
            a flowchart.js node connection string: "node_name->sub_node_name"
        """
        fc_conn_str = ''
        for connection in self.connections:
            if isinstance(connection, Node):
                specification = f'({self.connect_direction})' if self.connect_direction else ""
                fc_conn_str += f'{self.node_name}{specification}->{connection.node_name}\n'
        return fc_conn_str

    def _traverse(self, func, visited_flag) -> None:
        """_traverse walking the Node graph, visiting each Node, calls func(self).

        Args:
            func: function(node Node) -> bool: a function to be called on every Node.
                Stop traverse if func returns False
            visited_flag: something tags visited nodes.
                The graph of Nodes maybe not an acyclic graph.
                In this case, a visited_flag is necessary to
                avoid the infinite recursion.

        Returns:
            None
        """
        if self.__visited == visited_flag:
            return

        self.__visited = visited_flag
        to_be_continue = func(self)
        if not to_be_continue:
            return

        for c in self.connections:
            if isinstance(c, Node):
                c._traverse(func, visited_flag)

    def connect(self, sub_node, direction='') -> None:
        """connect: self->sub_node

        This method is a shorthand for node.connections.append(sub_node)

        Args:
            sub_node: another Node object to be connected.
            direction: connect direction: "left|right|top|bottom"

        Returns:
            None
        """
        if direction:
            self.set_connect_direction(direction)
        self.connections.append(sub_node)

    def set_connect_direction(self, connect_direction) -> None:
        """set connect direction

        The following directions are available and define the direction the connection will leave the node from:

        - "left"
        - "right"
        - "top"
        - "bottom"

        With custom connect_direction, node's fc_connection() will return
            thisNode(connect_direction)->nextNode
        Or,
            condNode(yes|no, connect_direction)->nextNode

        Args:
            connect_direction: custom connect_direction, None to omit direction specification.

        Returns:
            None
        """
        self.connect_direction = connect_direction

    def set_param(self, key: str, value: str):
        """ Set a `(param=value)`.
        See: https://github.com/adrai/flowchart.js/issues/115

        Args:
            key: str, key of param
            value: str, value of param

        Returns:
            None
        """
        if key and value:
            self.params[key] = value


class NodesGroup(Node):
    """
    NodesGroup is a special node that can contain other nodes.
    It makes a group of nodes look & behave like a single node.
    """

    def __init__(self, head_node: Node, tail_nodes=None):
        Node.__init__(self)
        if tail_nodes is None:
            tail_nodes = []
        self.head = head_node
        self.tails = tail_nodes

        self._fc_definitions = ''
        self._fc_connections = ''

        # parent node of NodesGroup calls fc_connection, getting connection to group head
        if self.head:
            self.node_name = self.head.node_name

    def set_head(self, head_node: Node):
        if head_node:
            self.head = head_node

            # parent node of NodesGroup calls fc_connection, getting connection to group head
            self.node_name = self.head.node_name

    def append_tails(self, tail_node: Node):
        self.tails.append(tail_node)

    def extend_tails(self, tail_nodes: list):
        self.tails.extend(tail_nodes)

    def fc_definition(self) -> str:
        self._refresh_fc()
        return self._fc_definitions

    def fc_connection(self) -> str:
        self._refresh_fc()
        return self._fc_connections

    def _traverse(self, func, visited_flag) -> None:
        self.head._traverse(func, visited_flag)

    def _inner_traverse(self, func, visited_flag) -> None:
        """
        Similar to _traverse, but only visit NodesGroup head to tails.
        """

        def func_stop_at_tails(node: Node, *args, **kwargs):
            if node in self.tails:
                return False
            return func(node, *args, **kwargs)

        self.head._traverse(func_stop_at_tails, visited_flag)

    def connect(self, sub_node, direction='') -> None:
        for t in self.tails:
            if isinstance(t, Node):
                if direction:
                    t.set_connect_direction(direction)
                t.connect(sub_node)

    def _clean_fc(self) -> None:
        """
        clean _fc_definitions & _fc_connections
        """
        self._fc_definitions = ''
        self._fc_connections = ''

    def _add_node_fc(self, node: Node) -> bool:
        """_add_node_fc visits a Node (in-group node), add it to NodesGroup.

        adds its fc_definition | fc_connection into self._fc_definitions | self._fc_connections.

        Args:
            node: visiting node

        Returns:
            always True
        """
        self._fc_definitions += node.fc_definition()
        self._fc_connections += node.fc_connection()

        return True

    def _refresh_fc(self) -> None:
        """
        refresh  _fc_definitions & _fc_connections
        """
        self._clean_fc()

        visited_flag = f'{id(self)}-{time.time()}-{uuid.uuid4()}'
        self._traverse(self._add_node_fc, visited_flag)

    def simplify(self) -> None:
        """
        simplify a NodesGroup

        It is common that a If without Else that contains only one line if-body,
        This kind of flow can be simplified:
            ConditionNode + OperationNode => OperationNode("if xx then operation")
        """
        pass


# flowchart.js flowchart DSL Nodes
# https://github.com/adrai/flowchart.js#node-syntax

class StartNode(Node):
    """StartNode is a Node subclass for flowchart.js `start` node
    """
    node_type = 'start'

    def __init__(self, name: str):
        super().__init__()
        self.node_name = f'st{self.id}'
        self.node_text = f'start {name}'


class EndNode(Node):
    """EndNode is a Node subclass for flowchart.js `end` node
    """
    node_type = 'end'

    def __init__(self, name: str):
        super().__init__()
        self.node_name = f'e{self.id}'
        self.node_text = f'end {name}'


class OperationNode(Node):
    """OperationNode is a Node subclass for flowchart.js `operation` node
    """
    node_type = 'operation'

    def __init__(self, operation: str):
        super().__init__()
        self.node_name = f'op{self.id}'
        self.node_text = f'{operation}'


class InputOutputNode(Node):
    """InputOutputNode is a Node subclass for flowchart.js `inputoutput` node
    """
    node_type = 'inputoutput'

    INPUT = 'input'
    OUTPUT = 'output'

    def __init__(self, input_or_output: str, content: str):
        super().__init__()
        self.node_name = f'io{self.id}'
        self.node_text = f'{input_or_output}: {content}'


class SubroutineNode(Node):
    """SubroutineNode is a Node subclass for flowchart.js `subroutine` node
    """
    node_type = 'subroutine'

    def __init__(self, subroutine: str):
        super().__init__()
        self.node_name = f'sub{self.id}'
        self.node_text = f'{subroutine}'


class ConditionNode(Node):
    """ConditionNode is a Node subclass for flowchart.js `condition` node
    """
    node_type = 'condition'

    def __init__(self, cond: str, align_next=True):
        """ConditionNode is a Node subclass for flowchart.js `condition` node.

        [v0.2.0] Set `align_next=False` to enable the `align-next=no` feature.
        See https://github.com/adrai/flowchart.js/issues/115 for details.

        Args:
            cond: str: the content of this ConditionNode
            align_next: bool: set False to write a `align-next=no` param. (default True)
        """
        super().__init__()
        self.node_name = f'cond{self.id}'
        self.node_text = f'{cond}'

        self.connection_yes = None
        self.connection_no = None

        if not align_next:
            self.no_align_next()

    def connect_yes(self, yes_node: Node, direction: str = ''):
        self.connection_yes = CondYN(self, CondYN.YES, yes_node)
        if direction:
            self.connection_yes.set_connect_direction(direction)
        self.connections.append(self.connection_yes)

    def connect_no(self, no_node: Node, direction: str = ''):
        self.connection_no = CondYN(self, CondYN.NO, no_node)
        if direction:
            self.connection_no.set_connect_direction(direction)
        self.connections.append(self.connection_no)

    def no_align_next(self):
        """set param: `(align-next=no)`

        See https://github.com/adrai/flowchart.js/issues/115

        Returns:
            None
        """
        self.set_param('align-next', 'no')


class CondYN(Node):
    """CondYesNode is a Node subclass for flowchart.js `cond(yes|no)->sub`

    It is not a actual node in flowchart.js, but a middle connection.
    There are no definition ("node_name=>node_type: node_text") for CondYN.
    It just offers a connection ("cond(yes|no)->sub").
    """

    YES = 'yes'
    NO = 'no'

    def __init__(self, cond: Node, yn: str, sub: Node = None):
        """CondYesNode is a Node subclass for flowchart.js `cond(yes|no)->sub`

        Args:
            cond: parent cond node
            yn: CondYN.YES or CondYN.NO
            sub: next_node, default None
        """
        super().__init__()

        self.cond = cond
        self.yn = yn
        self.sub = sub

        if isinstance(sub, Node):
            self.connections = [self.sub]

    def fc_definition(self) -> str:
        return ''

    def fc_connection(self) -> str:
        if self.sub:
            direction = f', {self.connect_direction}' if self.connect_direction else ""
            specification = f'({self.yn}{direction})'
            return f'{self.cond.node_name}{specification}->{self.sub.node_name}\n'
        return ""

    def connect(self, sub_node, direction='') -> None:
        if direction:
            self.set_connect_direction(direction)
        self.connections.append(sub_node)
        self.sub = sub_node
