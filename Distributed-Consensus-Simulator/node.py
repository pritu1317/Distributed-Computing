"""
node.py
-------
Definition of the Node class.

A Node represents one machine (server) inside the distributed cluster.
It can be a Leader or a Follower while it is online, or it can go
Offline (failure) and later recover.
"""

from config import STATE_FOLLOWER, STATE_LEADER, STATE_OFFLINE


class Node:
    """A single node in the distributed system."""

    def __init__(self, node_id):
        """Create a new node. Every node starts as an online follower."""
        self.node_id = node_id
        self.state = STATE_FOLLOWER   # LEADER / FOLLOWER / OFFLINE
        self.alive = True             # online flag
        self.vote = None              # "YES" / "NO" / None (has not voted)
        self.value = None             # value accepted once consensus is reached

    # ------------------------------------------------------------------
    # Role management
    # ------------------------------------------------------------------
    def make_leader(self):
        """Promote this node to Leader (only possible while online)."""
        if self.alive:
            self.state = STATE_LEADER

    def make_follower(self):
        """Demote this node to Follower (only possible while online)."""
        if self.alive:
            self.state = STATE_FOLLOWER

    # ------------------------------------------------------------------
    # Failure and recovery
    # ------------------------------------------------------------------
    def fail(self):
        """Simulate a node crash: it goes offline and loses its vote."""
        self.alive = False
        self.state = STATE_OFFLINE
        self.vote = None

    def recover(self):
        """Bring the node back online as a fresh Follower."""
        self.alive = True
        self.state = STATE_FOLLOWER
        self.vote = None
        self.value = None

    # ------------------------------------------------------------------
    # Consensus participation
    # ------------------------------------------------------------------
    def cast_vote(self, vote):
        """Record this node's vote for the current proposal."""
        if self.alive:
            self.vote = vote

    def accept_value(self, value):
        """Commit the agreed value to this node after consensus."""
        if self.alive:
            self.value = value

    def __repr__(self):
        """Developer-friendly string representation of the node."""
        return (f"Node(id={self.node_id}, state={self.state}, "
                f"alive={self.alive}, vote={self.vote}, value={self.value})")
