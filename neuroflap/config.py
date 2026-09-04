"""Zentrale Konfiguration: Fenster, Physik, Evolution und Farben."""

# --- Fenster ---
PANEL_WIDTH = 340
GAME_WIDTH = 800
WIDTH = GAME_WIDTH + PANEL_WIDTH
HEIGHT = 720
FPS = 60

# --- Vogel-Physik ---
BIRD_X = 190              # feste horizontale Position aller Vögel
BIRD_RADIUS = 11
GRAVITY = 0.45
FLAP_STRENGTH = -8.2
MAX_FALL_SPEED = 12.0

# --- Röhren & Schwierigkeit ---
PIPE_WIDTH = 74
PIPE_GAP = 200               # Start-Lückengröße (leicht)
PIPE_GAP_MIN = 155           # kleinste Lücke bei hohem Score
PIPE_SPEED = 3.0             # Grundtempo
PIPE_SPEED_MAX_BONUS = 2.0   # maximaler Tempo-Zuschlag
PIPE_SPACING = 330           # horizontaler Abstand zwischen zwei Röhren
PIPE_MIN_MARGIN = 70         # Mindestabstand der Lücke zu oben/unten
DIFF_GAP_PER_SCORE = 1.5     # Lücke verkleinert sich je Punkt (sanft)
DIFF_SPEED_PER_SCORE = 0.035 # Tempo steigt je Punkt (sanft)

# --- Neuronales Netz ---
INPUT_SIZE = 5
HIDDEN_SIZE = 6
OUTPUT_SIZE = 1

# --- Evolution ---
POPULATION_SIZE = 120
ELITE_COUNT = 6          # beste Netze unverändert übernehmen
MUTATION_RATE = 0.18     # Wahrscheinlichkeit pro Gewicht
MUTATION_STRENGTH = 0.4  # Streuung der Mutation
FITNESS_PIPE_BONUS = 25.0    # Fitness-Bonus je passierter Röhre
FITNESS_CENTER_BONUS = 0.6   # max. Bonus/Frame für zentrales Fliegen
MAX_ROUND_FRAMES = 4200      # Sicherheits-Limit je Runde (perfekte Vögel)

# --- Farben: modernes, kohärentes Dark-Theme (Slate / Twilight) ---
# Himmel-Verlauf der Spielfläche
COLOR_SKY_TOP = (17, 24, 45)         # tiefes Indigo
COLOR_SKY_MID = (30, 41, 72)         # Dämmerung
COLOR_SKY_BOTTOM = (51, 65, 105)     # heller Horizont
COLOR_GROUND = (13, 18, 33)
COLOR_GROUND_EDGE = (45, 212, 191)   # dünne Teal-Linie am Boden

# Akzente
COLOR_ACCENT = (56, 189, 248)        # Sky / Cyan
COLOR_ACCENT_2 = (45, 212, 191)      # Teal
COLOR_AMBER = (251, 191, 36)         # Anführer / Highlight

# Röhren (Emerald mit dezentem Verlauf)
COLOR_PIPE = (16, 185, 129)
COLOR_PIPE_DARK = (5, 90, 66)
COLOR_PIPE_LIGHT = (52, 211, 153)
COLOR_PIPE_CAP = (110, 231, 183)

# Vögel
COLOR_BIRD = (125, 185, 250)         # Schwarm dezent
COLOR_BIRD_BEST = (251, 191, 36)     # Anführer amber
COLOR_PLAYER = (56, 189, 248)

# Text & Panel
COLOR_TEXT = (226, 232, 240)
COLOR_TEXT_DIM = (148, 163, 184)
COLOR_PANEL_BG = (15, 23, 42)        # Slate-900
COLOR_CARD_BG = (30, 41, 59)         # Slate-800
COLOR_CARD_BORDER = (51, 65, 85)     # Slate-700

# Netz-Visualisierung
COLOR_NODE = (51, 65, 85)
COLOR_NODE_ON = (56, 189, 248)
COLOR_EDGE_POS = (56, 189, 248)
COLOR_EDGE_NEG = (244, 114, 130)

# Toggle / Mode-Switch
COLOR_TOGGLE_ON = (45, 212, 191)
COLOR_TOGGLE_OFF = (51, 65, 85)
COLOR_TOGGLE_KNOB = (241, 245, 249)
COLOR_MODE_ACTIVE = (56, 189, 248)
COLOR_MODE_INACTIVE = (30, 41, 59)

# Dezente Sterne
STAR_COUNT = 46
COLOR_STAR = (148, 163, 200)
