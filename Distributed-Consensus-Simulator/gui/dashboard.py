"""
gui/dashboard.py
----------------
Modern CustomTkinter dashboard for the Distributed Consensus Simulator.

Layout:
  +-------------------------------------------------------------+
  |  Header (dark navy): title + subtitle                       |
  +-----------+-------------------------------------------------+
  |  Sidebar  |  Statistics cards (TOTAL / ACTIVE / VOTES /    |
  |  controls |  CONSENSUS)                                     |
  |  + status |  NETWORK NODES (scrollable node cards)          |
  +-----------+-------------------------------------------------+
  |  EVENT LOG (dark panel)                                     |
  +-------------------------------------------------------------+
"""

import time

import customtkinter as ctk

from config import (
    COLOR_BACKGROUND,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_FOLLOWER,
    COLOR_HEADER_BG,
    COLOR_LEADER,
    COLOR_LOG_BG,
    COLOR_LOG_TEXT,
    COLOR_OFFLINE,
    COLOR_ONLINE,
    COLOR_PANEL_DARK,
    COLOR_SIDEBAR_BG,
    COLOR_TEXT_DARK,
    COLOR_TEXT_MUTED,
    CONSENSUS_FAILED,
    CONSENSUS_IDLE,
    CONSENSUS_REACHED,
    CONSENSUS_RUNNING,
    DEFAULT_NODE_COUNT,
    FONT_FAMILY,
    HOVER_FOLLOWER,
    HOVER_LEADER,
    HOVER_NEUTRAL,
    HOVER_OFFLINE,
    HOVER_ONLINE,
    LOG_FONT_FAMILY,
    STATE_FOLLOWER,
    STATE_LEADER,
    VOTE_DELAY_MS,
    VOTE_NO,
    VOTE_YES,
)
from consensus import ConsensusManager
from network import Network

# Number of node cards per row in the network view.
NODE_COLUMNS = 3


class Dashboard(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # ---- simulation core (model) ----
        self.network = Network()
        self.network.reset(DEFAULT_NODE_COUNT)
        self.consensus = ConsensusManager(self.network)
        self.voting_in_progress = False

        # ---- window setup ----
        self.configure(fg_color=COLOR_BACKGROUND)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---- build the interface ----
        self._build_header()
        self._build_sidebar()
        self._build_main_area()
        self._build_event_log()

        # ---- welcome messages ----
        self.log(f"System initialized with {len(self.network.nodes)} nodes.")
        self.log("Elect a leader to begin the simulation.")
        self.refresh()

    # ==================================================================
    # Header
    # ==================================================================
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_HEADER_BG, corner_radius=0,
                              height=90)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)

        texts = ctk.CTkFrame(header, fg_color="transparent")
        texts.pack(side="left", padx=28, pady=16)

        ctk.CTkLabel(
            texts,
            text="🌐  DISTRIBUTED CONSENSUS SIMULATOR",
            font=(FONT_FAMILY, 23, "bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w")

        ctk.CTkLabel(
            texts,
            text="Raft-style Distributed Systems Simulation",
            font=(FONT_FAMILY, 13),
            text_color="#9CA3AF",
        ).pack(anchor="w")

    # ==================================================================
    # Sidebar (control panel + system status)
    # ==================================================================
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR_BG,
                               corner_radius=0, width=300)
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="🎛️  CONTROL PANEL",
            font=(FONT_FAMILY, 16, "bold"), text_color="#FFFFFF",
        ).pack(anchor="w", padx=22, pady=(20, 14))

        # ---- proposal input ----
        ctk.CTkLabel(
            sidebar, text="📦  Proposal Value",
            font=(FONT_FAMILY, 12, "bold"), text_color="#D1D5DB",
        ).pack(anchor="w", padx=22)
        self.proposal_entry = ctk.CTkEntry(
            sidebar,
            placeholder_text="e.g. DATA-A",
            font=(FONT_FAMILY, 13),
            fg_color=COLOR_PANEL_DARK,
            text_color="#FFFFFF",
            placeholder_text_color="#9CA3AF",
            border_color="#374151",
            corner_radius=8,
            height=38,
        )
        self.proposal_entry.pack(fill="x", padx=22, pady=(6, 14))
        self.proposal_entry.bind("<Return>", lambda _e: self.start_consensus())

        # ---- control buttons ----
        self._make_button(sidebar, "➕  Add Node", self.add_node,
                          COLOR_ONLINE, HOVER_ONLINE)
        self._make_button(sidebar, "➖  Remove Node", self.remove_node,
                          COLOR_OFFLINE, HOVER_OFFLINE)
        self._make_button(sidebar, "👑  Elect Leader", self.elect_leader,
                          COLOR_LEADER, HOVER_LEADER)
        self._make_button(sidebar, "🚀  Start Consensus", self.start_consensus,
                          COLOR_FOLLOWER, HOVER_FOLLOWER)
        self._make_button(sidebar, "💥  Fail Random Node", self.fail_random_node,
                          COLOR_OFFLINE, HOVER_OFFLINE)
        self._make_button(sidebar, "🔄  Recover Nodes", self.recover_nodes,
                          COLOR_ONLINE, HOVER_ONLINE)
        self._make_button(sidebar, "♻️  Reset Simulation", self.reset_simulation,
                          "#6B7280", HOVER_NEUTRAL)

        # ---- divider ----
        divider = ctk.CTkFrame(sidebar, fg_color="#374151", height=1)
        divider.pack(fill="x", padx=22, pady=(16, 12))
        divider.pack_propagate(False)

        # ---- system status panel ----
        ctk.CTkLabel(
            sidebar, text="📊  SYSTEM STATUS",
            font=(FONT_FAMILY, 14, "bold"), text_color="#FFFFFF",
        ).pack(anchor="w", padx=22, pady=(0, 8))

        panel = ctk.CTkFrame(sidebar, fg_color=COLOR_PANEL_DARK,
                             corner_radius=10)
        panel.pack(fill="x", padx=22, pady=(0, 16))

        self.status_vars = {}
        for key in ("Leader", "Proposal", "Majority", "Phase"):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=5)
            ctk.CTkLabel(
                row, text=key.upper(),
                font=(FONT_FAMILY, 11, "bold"), text_color="#9CA3AF",
            ).pack(side="left")
            var = ctk.StringVar(value="-")
            ctk.CTkLabel(
                row, textvariable=var,
                font=(FONT_FAMILY, 11, "bold"), text_color="#FFFFFF",
            ).pack(side="right")
            self.status_vars[key] = var

    def _make_button(self, parent, text, command, color, hover_color):
        """Create a modern rounded button with a hover effect."""
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=color,
            hover_color=hover_color,
            text_color="#FFFFFF",
            corner_radius=8,
            height=40,
        )
        button.pack(fill="x", padx=22, pady=4)
        return button

    # ==================================================================
    # Main area (statistics + network nodes)
    # ==================================================================
    def _build_main_area(self):
        content = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND,
                               corner_radius=0)
        content.grid(row=1, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # ---- statistics cards ----
        stats = ctk.CTkFrame(content, fg_color="transparent")
        stats.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 6))
        for col in range(4):
            stats.grid_columnconfigure(col, weight=1, uniform="stat")

        self.total_nodes_label = self._make_stat_card(
            stats, 0, "TOTAL NODES", COLOR_TEXT_DARK)
        self.active_nodes_label = self._make_stat_card(
            stats, 1, "ACTIVE NODES", COLOR_ONLINE)
        self.total_votes_label, self.votes_sub_var = self._make_stat_card(
            stats, 2, "TOTAL VOTES", COLOR_FOLLOWER, with_sub=True)
        self.consensus_label, self.consensus_sub_var = self._make_stat_card(
            stats, 3, "CONSENSUS", COLOR_LEADER, with_sub=True)

        # ---- network nodes section ----
        section = ctk.CTkFrame(content, fg_color="transparent")
        section.grid(row=1, column=0, sticky="nsew", padx=18, pady=(6, 12))
        section.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            section, text="🖧  NETWORK NODES",
            font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXT_DARK,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.nodes_frame = ctk.CTkScrollableFrame(
            section, fg_color="transparent", corner_radius=0)
        self.nodes_frame.grid(row=1, column=0, sticky="nsew")
        for col in range(NODE_COLUMNS):
            self.nodes_frame.grid_columnconfigure(col, weight=1,
                                                  uniform="node")

    def _make_stat_card(self, parent, column, title, accent_color,
                        with_sub=False):
        """Create one white rounded statistics card; returns value label."""
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD_BG, corner_radius=12)
        card.grid(row=0, column=column, sticky="nsew", padx=6, pady=6)

        accent = ctk.CTkFrame(card, fg_color=accent_color, corner_radius=3,
                              height=4)
        accent.pack(fill="x", padx=16, pady=(14, 0))
        accent.pack_propagate(False)

        ctk.CTkLabel(
            card, text=title,
            font=(FONT_FAMILY, 11, "bold"), text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(10, 0))

        value_label = ctk.CTkLabel(
            card, text="0",
            font=(FONT_FAMILY, 30, "bold"), text_color=COLOR_TEXT_DARK,
        )
        value_label.pack(anchor="w", padx=16, pady=(0, 2))

        sub_var = None
        if with_sub:
            sub_var = ctk.StringVar(value="-")
            ctk.CTkLabel(
                card, textvariable=sub_var,
                font=(FONT_FAMILY, 11), text_color=COLOR_TEXT_MUTED,
            ).pack(anchor="w", padx=16, pady=(0, 12))
        else:
            ctk.CTkLabel(card, text=" ", font=(FONT_FAMILY, 11)).pack(
                anchor="w", padx=16, pady=(0, 12))

        if with_sub:
            return value_label, sub_var
        return value_label

    # ==================================================================
    # Event log
    # ==================================================================
    def _build_event_log(self):
        log_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND,
                                 corner_radius=0, height=200)
        log_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        log_frame.grid_propagate(False)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            log_frame, text="📜  EVENT LOG",
            font=(FONT_FAMILY, 13, "bold"), text_color=COLOR_TEXT_DARK,
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(4, 2))

        self.log_box = ctk.CTkTextbox(
            log_frame,
            fg_color=COLOR_LOG_BG,
            text_color=COLOR_LOG_TEXT,
            font=(LOG_FONT_FAMILY, 12),
            corner_radius=10,
            state="disabled",
            wrap="word",
        )
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 14))

        # Colored tags to highlight important events.
        self.log_box.tag_config("error", foreground="#F87171")
        self.log_box.tag_config("success", foreground="#34D399")
        self.log_box.tag_config("leader", foreground="#FBBF24")
        self.log_box.tag_config("info", foreground="#93C5FD")

    def log(self, message):
        """Append a timestamped line to the event log."""
        timestamp = time.strftime("%H:%M:%S")
        tag = self._tag_for(message)
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {message}\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    @staticmethod
    def _tag_for(message):
        """Pick a color tag based on the contents of a log message."""
        text = message.lower()
        if message.startswith("ERROR") or "consensus failed" in text:
            return "error"
        if "elected as leader" in text:
            return "leader"
        if "consensus reached" in text:
            return "success"
        if ("proposed" in text or " recovered" in text or " failed" in text
                or "joined" in text or "removed" in text):
            return "info"
        return ""

    # ==================================================================
    # Node cards
    # ==================================================================
    def _rebuild_node_cards(self):
        """Recreate one card per node inside the scrollable frame."""
        for child in self.nodes_frame.winfo_children():
            child.destroy()
        for index, node in enumerate(self.network.nodes):
            card = self._make_node_card(node)
            card.grid(row=index // NODE_COLUMNS,
                      column=index % NODE_COLUMNS,
                      sticky="nsew", padx=6, pady=6)

    def _make_node_card(self, node):
        """Build a modern card showing one node's state, vote and value."""
        if node.state == STATE_LEADER:
            role_color = COLOR_LEADER
            border_width = 2
        elif node.state == STATE_FOLLOWER:
            role_color = COLOR_FOLLOWER
            border_width = 1
        else:
            role_color = COLOR_OFFLINE
            border_width = 1
        border_color = role_color if node.state == STATE_LEADER else COLOR_BORDER

        card = ctk.CTkFrame(
            self.nodes_frame,
            fg_color=COLOR_CARD_BG,
            corner_radius=12,
            border_width=border_width,
            border_color=border_color,
        )

        # top row: node id + online status
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            top, text=f"NODE {node.node_id}",
            font=(FONT_FAMILY, 15, "bold"), text_color=COLOR_TEXT_DARK,
        ).pack(side="left")
        status_text = "● ONLINE" if node.alive else "● OFFLINE"
        status_color = COLOR_ONLINE if node.alive else COLOR_OFFLINE
        ctk.CTkLabel(
            top, text=status_text,
            font=(FONT_FAMILY, 11, "bold"), text_color=status_color,
        ).pack(side="right")

        # role chip
        ctk.CTkLabel(
            card, text=node.state,
            font=(FONT_FAMILY, 11, "bold"), text_color="#FFFFFF",
            fg_color=role_color, corner_radius=6,
        ).pack(anchor="w", padx=14, pady=(4, 8))

        # vote row
        vote_row = ctk.CTkFrame(card, fg_color="transparent")
        vote_row.pack(fill="x", padx=14, pady=(0, 2))
        ctk.CTkLabel(
            vote_row, text="Vote",
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED,
        ).pack(side="left")
        if node.vote == VOTE_YES:
            vote_text, vote_color = VOTE_YES, COLOR_ONLINE
        elif node.vote == VOTE_NO:
            vote_text, vote_color = VOTE_NO, COLOR_OFFLINE
        else:
            vote_text, vote_color = "—", COLOR_TEXT_MUTED
        ctk.CTkLabel(
            vote_row, text=vote_text,
            font=(FONT_FAMILY, 12, "bold"), text_color=vote_color,
        ).pack(side="right")

        # value row
        value_row = ctk.CTkFrame(card, fg_color="transparent")
        value_row.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkLabel(
            value_row, text="Value",
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MUTED,
        ).pack(side="left")
        ctk.CTkLabel(
            value_row, text=node.value or "—",
            font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXT_DARK,
        ).pack(side="right")

        return card

    # ==================================================================
    # Refresh / statistics
    # ==================================================================
    def refresh(self):
        """Update every dynamic label, card and status value."""
        nodes = self.network.nodes
        active = self.network.get_active_nodes()

        # statistics cards
        self.total_nodes_label.configure(text=str(len(nodes)))
        self.active_nodes_label.configure(text=str(len(active)))

        yes_votes = self.consensus.count_yes_votes()
        total_votes = len(self.consensus.votes)
        self.total_votes_label.configure(text=str(total_votes))
        self.votes_sub_var.set(f"YES {yes_votes}  •  NO {total_votes - yes_votes}")

        majority = self.consensus.calculate_majority(len(active))
        labels = {
            CONSENSUS_IDLE: "IDLE",
            CONSENSUS_RUNNING: "RUNNING",
            CONSENSUS_REACHED: "REACHED",
            CONSENSUS_FAILED: "FAILED",
        }
        colors = {
            CONSENSUS_IDLE: COLOR_TEXT_MUTED,
            CONSENSUS_RUNNING: COLOR_FOLLOWER,
            CONSENSUS_REACHED: COLOR_ONLINE,
            CONSENSUS_FAILED: COLOR_OFFLINE,
        }
        self.consensus_label.configure(text=labels[self.consensus.state])
        self.consensus_label.configure(
            text_color=colors[self.consensus.state])
        self.consensus_sub_var.set(
            f"Need {majority} YES of {len(active)} active")

        # system status panel
        leader = self.consensus.leader
        if leader is not None and not leader.alive:
            leader = None
        self.status_vars["Leader"].set(
            f"Node {leader.node_id}" if leader else "None")
        self.status_vars["Proposal"].set(self.consensus.proposal or "None")
        self.status_vars["Majority"].set(str(majority))
        self.status_vars["Phase"].set(labels[self.consensus.state])

        # node cards
        self._rebuild_node_cards()

    # ==================================================================
    # Control actions
    # ==================================================================
    def add_node(self):
        if self.voting_in_progress:
            return
        node = self.network.add_node()
        self.log(f"Node {node.node_id} joined the network.")
        self.refresh()

    def remove_node(self):
        if self.voting_in_progress:
            return
        node = self.network.remove_node()
        if node is None:
            self.log("ERROR: Cannot remove nodes - at least "
                     f"1 node must remain.")
            return
        if self.consensus.leader is node:
            self.consensus.leader = None
        self.log(f"Node {node.node_id} removed from the network.")
        self.refresh()

    def elect_leader(self):
        if self.voting_in_progress:
            return
        leader = self.consensus.elect_leader()
        if leader is None:
            self.log("ERROR: No active nodes available for election.")
            return
        self.log(f"Node {leader.node_id} elected as Leader.")
        self.refresh()

    def start_consensus(self):
        if self.voting_in_progress:
            return

        # a living leader is required to broadcast a proposal
        self.consensus.clear_leader_if_dead()
        if self.consensus.leader is None:
            self.log("ERROR: No leader elected. Elect a leader first.")
            return

        # a proposal value is required
        value = self.proposal_entry.get().strip()
        if not value:
            self.log("ERROR: Enter a proposal value first.")
            return

        self.consensus.create_proposal(value)
        self.log(f"Leader proposed: {value}")

        voters = self.consensus.start_voting()
        self.log(f"Majority required: {self.consensus.majority} of "
                 f"{len(voters)} active nodes.")

        self.voting_in_progress = True
        self.refresh()
        self._cast_next_vote(voters, 0)

    def _cast_next_vote(self, voters, index):
        """Cast votes one by one with a small delay for a live visual demo."""
        if index < len(voters):
            node = voters[index]
            vote = self.consensus.request_vote(node)
            if vote is not None:
                self.log(f"Node {node.node_id} voted {vote}.")
                self.refresh()
            self.after(VOTE_DELAY_MS,
                       lambda: self._cast_next_vote(voters, index + 1))
        else:
            success = self.consensus.validate_consensus()
            if success:
                self.log("Consensus reached. Value committed to all "
                         "active nodes.")
            else:
                self.log("ERROR: Consensus failed. Majority not reached.")
            self.voting_in_progress = False
            self.refresh()

    def fail_random_node(self):
        if self.voting_in_progress:
            return
        node = self.network.fail_random_node()
        if node is None:
            self.log("ERROR: No active node available to fail.")
            return
        was_leader = self.consensus.leader is node
        self.consensus.clear_leader_if_dead()
        if was_leader:
            self.log(f"Node {node.node_id} failed. The Leader is down - "
                     "elect a new leader.")
        else:
            self.log(f"Node {node.node_id} failed.")
        self.refresh()

    def recover_nodes(self):
        if self.voting_in_progress:
            return
        offline = [n for n in self.network.nodes if not n.alive]
        if not offline:
            self.log("All nodes are already online.")
            return
        self.network.recover_all_nodes()
        for node in offline:
            self.log(f"Node {node.node_id} recovered.")
        self.refresh()

    def reset_simulation(self):
        if self.voting_in_progress:
            self.log("ERROR: Wait for the current voting round to finish.")
            return
        self.network.reset(DEFAULT_NODE_COUNT)
        self.consensus.reset()
        self.proposal_entry.delete(0, "end")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.log(f"System initialized with {len(self.network.nodes)} nodes.")
        self.refresh()
