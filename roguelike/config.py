"""Zentrale Konfiguration: Größen, Farben und Spiel-Tuning an einem Ort."""

# --- Karte (in Tiles) ---
MAP_WIDTH = 58
MAP_HEIGHT = 36

# --- Darstellung ---
TILE_SIZE = 22          # Kantenlänge eines Tiles in Pixeln
PANEL_HEIGHT = 150      # Höhe des unteren Info-Panels
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE + PANEL_HEIGHT
FPS = 60
MESSAGE_LOG_LINES = 3

# --- Dungeon-Generierung ---
MAX_ROOMS = 18
ROOM_MIN_SIZE = 6
ROOM_MAX_SIZE = 12
MAX_MONSTERS_PER_ROOM = 3
MAX_ITEMS_PER_ROOM = 2

# --- Sichtfeld ---
FOV_RADIUS = 8

# --- Gegner-KI ---
# Wie viele Runden ein Gegner die zuletzt bekannte Spielerposition verfolgt,
# nachdem er den Spieler aus den Augen verloren hat.
ENEMY_MEMORY_TURNS = 6

# --- Spielziel & Items ---
DEPTH_GOAL = 8          # Ab dieser Ebene führt die Treppe zum Sieg
POTION_HEAL = 8         # Heilung pro Trank

# --- Farben (R, G, B) ---
COLOR_BG = (8, 8, 14)
COLOR_DARK_WALL = (24, 22, 34)
COLOR_DARK_GROUND = (16, 16, 26)
COLOR_LIGHT_WALL = (86, 74, 112)
COLOR_LIGHT_GROUND = (52, 48, 74)

COLOR_PLAYER = (120, 230, 180)
COLOR_STAIRS = (240, 210, 90)

COLOR_TEXT = (220, 220, 235)
COLOR_TEXT_DIM = (130, 130, 160)
COLOR_HP_BAR = (200, 60, 70)
COLOR_HP_BAR_BG = (60, 24, 30)
COLOR_PANEL_BG = (14, 14, 22)
COLOR_ACCENT = (150, 120, 220)

# Nachrichtenfarben
COLOR_MSG_INFO = (200, 200, 215)
COLOR_MSG_GOOD = (120, 220, 140)
COLOR_MSG_BAD = (230, 110, 110)
COLOR_MSG_WARN = (235, 200, 100)
