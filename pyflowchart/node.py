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
from typing import List, TypeVar, Optional

# AsNode is a TypeVar for Node and its subclasses
AsNode = TypeVar('AsNode', bound='Node')

__DEBUG = False


def debug(*args, **kwargs):
    if not __DEBUG:
        return
    import sys
    print('DBG', *args, **kwargs, file=sys.stderr)


class Node(object):
    """Node is an abstract class for kinds of flowchart node.
    """
    node_type = 'node'  # flowchart.js Node Syntax: nodeType

    # object id: an iterator
    # each entities call next(self._node_id) to get an ID.
    # XXX: I am not fully sure that this is thread-safe.
    _node_id = itertools.count(0)

    def __init__(self):
        self.node_name = ''  # flowchart.js Node Syntax: nodeName
        self.node_text = ''  # flowchart.js Node Syntax: nodeText
        self.connections: List[Connection] = []  # connected (next / sub) nodes.

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
            if isinstance(connection, Connection):
                connection.params.append(self.connect_direction)
                fc_conn_str += connection.fc_connection(self)
            else:
                # debug(f'Warning: Node.fc_connection: unexpected connection: {connection}')
                pass
        return fc_conn_str

    def _traverse(self, func, visited_flag) -> None:
        """_traverse walking the Node graph, visiting each Node, calls func(self).

        Args:
            func: function(node: Node) -> bool: a function to be called on every Node.
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
        # debug(f"Node._traverse: {self}, func={func}, visited_flag={visited_flag}")
        to_be_continue = func(self)
        if not to_be_continue:
            return

        for c in self.connections:
            # debug(f"Node._traverse: {self} to {c}")
            if isinstance(c, Connection) and isinstance(c.next_node, Node):
                c.next_node._traverse(func, visited_flag)
            else:
                # debug(f'Warning: Node._traverse: unexpected connection: {c}')
                pass

    def connect(self, sub_node: AsNode, direction='') -> None:
        """connect: self->sub_node

        This method is a shorthand for node.connections.append(Connection(sub_node))

        Args:
            sub_node: another Node object to be connected.
            direction: connect direction: "left|right|top|bottom"

        Returns:
            None
        """
        connection = Connection(sub_node, direction)
        self.connections.append(connection)

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

    def __repr__(self):
        return f'<Node({self.node_name}): {self.node_text}>'


class Connection(object):
    """Connection is a middle connection between two nodes.

    A Node has a list of connections, each connection is a Connection object,
    which contains a next_node and some params:

        thisNode(params...)->nextNode

    Note: `thisNode` is not contained in Connection object,
    instead, the Connection object is contained in `thisNode`.
    This is in order to avoid the recursion reference.
    """
    next_node: Node = None
    params: List[str] = []

    def __init__(self, next_node: Node, *params: str):
        self.next_node = next_node
        self.params = list(params)

    def fc_connection(self, src_node: Node) -> str:
        """fc_connection returns the flowchart.js node connection string of current Connection.

        Args:
            src_node: source node of this connection

        Returns:
            a flowchart.js node connection string: "node_name->sub_node_name"
        """
        if not isinstance(src_node, Node):
            # debug(f"Connection.fc_connection: unexpected src_node: {src_node}, return empty string")
            return ""
        # assert isinstance(self.next_node, Node) or self.next_node is None

        fc_conn_str = ''

        if isinstance(self.next_node, Node):
            if not self.next_node.node_name:
                return ''
            params = ','.join(set(filter(lambda x: x, self.params)))
            specification = f'({params})' if params else ''
            fc_conn_str += f'{src_node.node_name}{specification}->{self.next_node.node_name}\n'
        # else (self.next_node is None): fc_conn_str = ''

        # debug(f"Connection.fc_connection: {fc_conn_str}")

        return fc_conn_str

    def set_param(self, param: str):
        self.params.append(param)

    def __repr__(self):
        return f'<Connection: to={self.next_node}, params={self.params}>'


class NodesGroup(Node):
    """
    NodesGroup is a special node that can contain other nodes.
    It makes a group of nodes look & behave like a single node.

    NodesGroup.connections is unused.
    """

    def __init__(self, head_node: Optional[Node], tail_nodes=None):
        Node.__init__(self)
        # special case: ParseProcessGraph: head == None
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
                t.connect(sub_node, direction)

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
        # debug(f"NodesGroup._add_node_fc: {node}, fc_definition={node.fc_definition()}, fc_connection={node.fc_connection()}")
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

        It is common that an If without Else that contains only one line if-body,
        This kind of flow can be simplified:
            ConditionNode + OperationNode => OperationNode("if xx then operation")
        """
        pass

    @property
    def node_name(self):
        """
        node_name of NodesGroup is the node_name of its head node.

        Connection.fc_connection() relies on this property.
        """
        try:
            return self.head.node_name
        except AttributeError:  # before NodesGroup.__init__ done
            return ''

    @node_name.setter
    def node_name(self, value):
        # do nothing, proxy setting head's property is not only nonsense,
        # but also wrong:
        #  self.__init__() -> Node.__init__() -> self.node_name = ''
        # this breaks the head node_name setting.
        return


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

        self.connection_yes: Optional[Connection] = None
        self.connection_no: Optional[Connection] = None

        if not align_next:
            self.no_align_next()

    def connect_yes(self, yes_node: Optional[Node], direction: str = ''):
        # yes_node is optional due to the virtual node is connecting to None
        condyn = CondYN(self, CondYN.YES, yes_node)
        self.connection_yes = Connection(condyn, 'yes', direction)
        self.connections.append(self.connection_yes)

    def connect_no(self, no_node: Optional[Node], direction: str = ''):
        condyn = CondYN(self, CondYN.NO, no_node)
        self.connection_no = Connection(condyn, 'no', direction)
        self.connections.append(self.connection_no)

    def no_align_next(self):
        """set param: `(align-next=no)`

        See https://github.com/adrai/flowchart.js/issues/115

        Returns:
            None
        """
        self.set_param('align-next', 'no')


class TransparentNode(Node):
    """TransparentNode is a Node subclass that
    connects its parent and child directly.

        parent_node -> transparent_node -> child_node

    Resulting in a flowchart.js flowchart like this:

        parent_node->child_node

    This is useful to work with NodesGroups as a head or tail.

    For example, consider a `if` block without `else`:

        start()
        if cond:
            some_operation
        end()

    In the process of parse(), for the if-branch, we get an OperationNode("some_operation")
    and this node will be added to the tails.
    However, the else-branch is empty, but we still need to connect the `if` and `end`.
    So we add a TransparentNode to the tails, and connect it to the `end`.

    Similarly, Loops need this as a virtual tail, and MatchCases need this as a virtual head.

    Notice: A TransparentNode has a single parent and a single child.
            Later call to connect() will overwrite the previous child & connection & params.
    """

    def __init__(self, parent: Node, child: Node = None, connect_params: List[str] = None):
        """CondYesNode is a Node subclass for flowchart.js `cond(yes|no)->sub`

        Args:
            parent: parent cond node
            child: next_node, default None
            connect_params: params of connection, default None
        """
        super().__init__()

        self.parent = parent
        self.child = child
        self.connect_params = connect_params or []
        self.connection = Connection(child, *self.connect_params)

    @property
    def connections(self):
        return [self.connection]

    @connections.setter
    def connections(self, value):
        """Should never be used.
        Makes compiler happy. (`Node.__init__` writes this.)
        """
        if not value:
            return
        try:
            self.connection = value[0]
        except IndexError:
            pass

    def fc_definition(self) -> str:
        return ''

    def fc_connection(self) -> str:
        assert isinstance(self.parent, Node)
        assert isinstance(self.connection, Connection)
        return self.connection.fc_connection(self.parent)

    def connect(self, sub_node, *params: str) -> None:
        self.child = sub_node
        self.connect_params.extend(params)
        self.connection = Connection(sub_node, *self.connect_params)

    # TransparentNode has no name.
    # It is a virtual node, and it is not a real node in flowchart.js.
    # So it has no name, as well as no definition.
    # It just offers a connection parent->child.
    #
    # @property
    # def node_name(self):
    #     try:
    #         return self.child.node_name
    #     except AttributeError:
    #         return ''
    #
    # @node_name.setter
    # def node_name(self, value):
    #     return  # do nothing, see NodesGroup.node_name.setter for reason


class CondYN(TransparentNode):
    """CondYesNode is a Node subclass for flowchart.js `cond(yes|no)->sub`

    It is not an actual node in flowchart.js, but a middle connection.
    There are no definition ("node_name=>node_type: node_text") for CondYN.
    It just offers a connection ("cond(yes|no)->sub").

    CondYN is TransparentNode:

    CondYN is a subclass of Node directly in the history.
    After the introduction of TransparentNode,
    we rewrote CondYN as a subclass of TransparentNode,
    keeps the same interface as before, for compatibility.

    New codes should use TransparentNode instead of CondYN.
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
        TransparentNode.__init__(self, cond, sub, [yn])
        # self.node_name = f'<CondYN: parent={cond}>'

    # old interface

    @property
    def cond(self):
        return self.parent

    @property
    def yn(self):
        return ",".join(self.connect_params) if self.connect_params else ""

    @property
    def sub(self):
        return self.child

    def connect(self, sub_node, *params: str) -> None:
        # Historically, CondYN.connect() keeps the previous params.
        # Actually, TransparentNode.connect() do extend the params too.
        # So this is a verbose.
        params = list(params)
        params.extend(self.connect_params)

        TransparentNode.connect(self, sub_node, *params)
