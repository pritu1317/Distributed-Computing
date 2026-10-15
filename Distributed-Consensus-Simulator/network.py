"""
network.py
----------
The Network class manages the whole collection of distributed nodes.

It provides operations to grow/shrink the cluster, query active nodes
and simulate random failures and recovery - the "plumbing" of the
distributed system.
"""

import random

from config import DEFAULT_NODE_COUNT, MIN_NODES, STATE_LEADER
from node import Node


class Network:
    """Container that owns and manages all nodes of the cluster."""

    def __init__(self):
        self.nodes = []
        self._next_node_id = 1  # IDs are generated automatically

    # ------------------------------------------------------------------
    # Cluster management
    # ------------------------------------------------------------------
    def add_node(self):
        """Create a new node with an automatically generated ID."""
        node = Node(self._next_node_id)
        self._next_node_id += 1
        self.nodes.append(node)
        return node

    def remove_node(self):
        """
        Remove the most recently added node.

        Returns the removed node, or None if removal is not allowed
        (a minimum of MIN_NODES nodes must always remain).
        """
        if len(self.nodes) <= MIN_NODES:
            return None
        return self.nodes.pop()

    def get_node(self, node_id):
        """Return the node with the given ID (or None)."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def get_leader(self):
        """Return the current leader node, or None if there is no leader."""
        for node in self.nodes:
            if node.alive and node.state == STATE_LEADER:
                return node
        return None

    # ------------------------------------------------------------------
    # Active node helpers
    # ------------------------------------------------------------------
    def get_active_nodes(self):
        """Return a list of all online (alive) nodes."""
        return [node for node in self.nodes if node.alive]

    def get_random_active_node(self):
        """Return a random online node, or None if no node is online."""
        active = self.get_active_nodes()
        return random.choice(active) if active else None

    # ------------------------------------------------------------------
    # Failure and recovery
    # ------------------------------------------------------------------
    def fail_random_node(self):
        """Crash a random online node. Returns the failed node (or None)."""
        node = self.get_random_active_node()
        if node is not None:
            node.fail()
        return node

    def recover_all_nodes(self):
        """Bring every offline node back online as a Follower."""
        for node in self.nodes:
            if not node.alive:
                node.recover()

    # ------------------------------------------------------------------
    # Simulation lifecycle
    # ------------------------------------------------------------------
    def reset(self, node_count=DEFAULT_NODE_COUNT):
        """Rebuild the cluster: `node_count` fresh online followers."""
        self.nodes = []
        self._next_node_id = 1
        for _ in range(node_count):
            self.add_node()
