"""
consensus.py
------------
The ConsensusManager implements a simplified Raft-style consensus
protocol on top of the Network:

1. Leader election  - one random active node is chosen as Leader,
                      every other active node becomes a Follower.
2. Proposal         - the Leader broadcasts a value to the cluster.
3. Voting           - each active node replies with a YES/NO vote.
4. Majority         - consensus succeeds when the number of YES votes
                      is >= majority, where

                          majority = (active_nodes // 2) + 1

5. Commit           - on success the value is accepted by every
                      active node; otherwise the round fails.
"""

import random

from config import (
    CONSENSUS_FAILED,
    CONSENSUS_IDLE,
    CONSENSUS_REACHED,
    CONSENSUS_RUNNING,
    VOTE_NO,
    VOTE_YES,
    VOTE_YES_PROBABILITY,
)


class ConsensusManager:
    """Coordinates leader election and proposal voting rounds."""

    def __init__(self, network):
        self.network = network
        self.reset()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def reset(self):
        """Clear the proposal, votes, majority and current leader."""
        self.proposal = None
        self.votes = {}          # node_id -> "YES" / "NO"
        self.majority = 0        # YES votes required to win
        self.state = CONSENSUS_IDLE
        self.leader = None

    # ------------------------------------------------------------------
    # 1. Leader election
    # ------------------------------------------------------------------
    def elect_leader(self):
        """
        Pick a random active node as the new Leader and demote every
        other active node to Follower. Returns the new leader (or None
        if no active node is available). A new election term clears all
        previous votes, just like a new term in real Raft.
        """
        candidate = self.network.get_random_active_node()
        if candidate is None:
            return None

        for node in self.network.nodes:
            node.vote = None      # new term -> old votes are forgotten
        self.votes = {}

        for node in self.network.get_active_nodes():
            node.make_follower()
        candidate.make_leader()
        self.leader = candidate
        return candidate

    def clear_leader_if_dead(self):
        """Forget the leader reference if the leader has failed."""
        if self.leader is not None and not self.leader.alive:
            self.leader = None

    # ------------------------------------------------------------------
    # 2. Proposal
    # ------------------------------------------------------------------
    def create_proposal(self, value):
        """Store a new proposal value and clear the previous round."""
        self.proposal = value
        self.votes = {}
        self.state = CONSENSUS_IDLE
        for node in self.network.nodes:
            node.vote = None
            node.value = None
        return self.proposal

    # ------------------------------------------------------------------
    # 3. Voting
    # ------------------------------------------------------------------
    def start_voting(self):
        """
        Begin a voting round: compute the majority from the currently
        active nodes and return the list of nodes allowed to vote.
        """
        active = self.network.get_active_nodes()
        self.majority = self.calculate_majority(len(active))
        self.votes = {}
        self.state = CONSENSUS_RUNNING
        return active

    @staticmethod
    def calculate_majority(active_count):
        """majority = (active_nodes // 2) + 1"""
        return (active_count // 2) + 1

    def request_vote(self, node):
        """
        Ask one active node to vote on the current proposal.

        A node votes YES with probability VOTE_YES_PROBABILITY (a
        simplified model of followers that usually agree but can
        reject a proposal). Returns the cast vote, or None if the node
        is offline and therefore cannot vote.
        """
        if not node.alive:
            return None
        vote = VOTE_YES if random.random() < VOTE_YES_PROBABILITY else VOTE_NO
        node.cast_vote(vote)
        self.votes[node.node_id] = vote
        return vote

    def count_yes_votes(self):
        """Return how many YES votes have been collected."""
        return sum(1 for vote in self.votes.values() if vote == VOTE_YES)

    # ------------------------------------------------------------------
    # 4. Validation
    # ------------------------------------------------------------------
    def validate_consensus(self):
        """
        Decide the outcome of the round: REACHED when the YES votes are
        >= majority, otherwise FAILED. On success the proposal value is
        committed (accepted) to every active node.
        """
        success = self.count_yes_votes() >= self.majority
        self.state = CONSENSUS_REACHED if success else CONSENSUS_FAILED
        if success:
            for node in self.network.get_active_nodes():
                node.accept_value(self.proposal)
        return success
