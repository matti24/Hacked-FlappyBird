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

# --- Röhren ---
PIPE_WIDTH = 74
PIPE_GAP = 180
PIPE_SPEED = 3.2
PIPE_SPACING = 330       # horizontaler Abstand zwischen zwei Röhren
PIPE_MIN_MARGIN = 70     # Mindestabstand der Lücke zu oben/unten

# --- Neuronales Netz ---
INPUT_SIZE = 5
HIDDEN_SIZE = 8
OUTPUT_SIZE = 1

# --- Evolution ---
POPULATION_SIZE = 150
ELITE_COUNT = 4          # beste Netze unverändert übernehmen
MUTATION_RATE = 0.15     # Wahrscheinlichkeit pro Gewicht
MUTATION_STRENGTH = 0.6  # Streuung der Mutation

# --- Farben (R, G, B) ---
COLOR_BG_TOP = (12, 16, 34)
COLOR_BG_BOTTOM = (6, 8, 20)
COLOR_PIPE = (86, 204, 140)
COLOR_PIPE_EDGE = (140, 240, 180)
COLOR_BIRD = (120, 200, 255)
COLOR_BIRD_BEST = (255, 214, 90)
COLOR_GROUND = (22, 26, 44)

COLOR_TEXT = (228, 230, 245)
COLOR_TEXT_DIM = (140, 146, 178)
COLOR_ACCENT = (150, 120, 240)
COLOR_ACCENT_2 = (90, 210, 235)
COLOR_PANEL_BG = (14, 16, 30)

# Netz-Visualisierung
COLOR_NODE = (60, 66, 96)
COLOR_EDGE_POS = (90, 210, 235)
COLOR_EDGE_NEG = (235, 96, 120)
