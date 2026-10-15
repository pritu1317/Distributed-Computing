"""
config.py
---------
Central configuration file for the Distributed Consensus Simulator.

All application-wide constants (window settings, simulation parameters,
node states, votes and the color palette) live here so the rest of the
codebase stays clean and easy to tweak.
"""

# ---------------------------------------------------------------------------
# Application settings
# ---------------------------------------------------------------------------
APP_TITLE = "Distributed Consensus Simulator"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 1100
MIN_WINDOW_HEIGHT = 720

# ---------------------------------------------------------------------------
# Simulation defaults
# ---------------------------------------------------------------------------
DEFAULT_NODE_COUNT = 5     # number of nodes at startup / after a reset
MIN_NODES = 1              # never allow the user to remove every node

# Probability that an active node votes YES for a proposal.
# In a real Raft cluster a follower usually votes YES, but may vote NO
# (e.g. its term is newer). This constant lets us simulate both outcomes.
VOTE_YES_PROBABILITY = 0.8

# Delay (milliseconds) between two vote events while a round is running,
# so the user can watch the votes arriving in the event log in real time.
VOTE_DELAY_MS = 550

# ---------------------------------------------------------------------------
# Node states
# ---------------------------------------------------------------------------
STATE_LEADER = "LEADER"
STATE_FOLLOWER = "FOLLOWER"
STATE_OFFLINE = "OFFLINE"

# ---------------------------------------------------------------------------
# Vote options
# ---------------------------------------------------------------------------
VOTE_YES = "YES"
VOTE_NO = "NO"

# ---------------------------------------------------------------------------
# Consensus (round) states
# ---------------------------------------------------------------------------
CONSENSUS_IDLE = "IDLE"       # nothing has happened yet
CONSENSUS_RUNNING = "RUNNING" # votes are being collected
CONSENSUS_REACHED = "REACHED" # majority voted YES
CONSENSUS_FAILED = "FAILED"   # majority not reached

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_FAMILY = "Segoe UI"
LOG_FONT_FAMILY = "Consolas"

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
COLOR_HEADER_BG = "#111827"   # dark navy - header
COLOR_SIDEBAR_BG = "#1F2937"  # dark grey - sidebar
COLOR_PANEL_DARK = "#111827"  # darker panels on the sidebar
COLOR_LOG_BG = "#111827"      # event log background
COLOR_LOG_TEXT = "#D1D5DB"    # event log text

COLOR_BACKGROUND = "#F4F7FB"  # light grey - main background
COLOR_CARD_BG = "#FFFFFF"     # white - cards
COLOR_BORDER = "#E5E7EB"      # light border for cards

COLOR_TEXT_DARK = "#1F2937"   # primary text
COLOR_TEXT_MUTED = "#6B7280"  # secondary text

COLOR_LEADER = "#F59E0B"      # orange/yellow - leader
COLOR_FOLLOWER = "#3498DB"    # blue - follower
COLOR_ONLINE = "#10B981"      # green - online / consensus YES
COLOR_OFFLINE = "#EF4444"     # red - offline / consensus NO

# Darker variants used for button hover effects
HOVER_ONLINE = "#0E9F6E"
HOVER_OFFLINE = "#DC2626"
HOVER_LEADER = "#D97706"
HOVER_FOLLOWER = "#2980B9"
HOVER_NEUTRAL = "#4B5563"
