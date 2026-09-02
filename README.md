# 🗡️ Dark Depths

Ein prozedurales Roguelike mit **smarter Gegner-KI**, geschrieben in Python mit `pygame-ce`.
Jeder Abstieg erzeugt einen neuen Dungeon – erkunde ihn, kämpfe gegen Kobolde, Orks und Trolle
und steige so tief wie möglich hinab.

![Vorschau](docs/preview.png)

## ✨ Features

- **Prozedural generierte Dungeons** – zufällige Räume, mit Gängen verbunden; jeder Durchlauf ist neu.
- **Smarte Gegner-KI** – Zustandsautomat (*wandern → verfolgen → angreifen*) mit
  A*-Wegfindung und Sichtlinien-Prüfung. Gegner **merken sich die zuletzt bekannte
  Position** und suchen dich noch einige Runden, nachdem sie dich aus den Augen verloren haben.
- **Field of View / Fog of War** – Recursive Shadowcasting: du siehst nur, was im Licht liegt;
  erkundete Bereiche bleiben abgedunkelt sichtbar.
- **Rundenbasierter Kampf** – Angriff/Verteidigung, verschiedene Gegnertypen, Heiltränke.
- **Mehrere Ebenen** – steige über Treppen (`>`) tiefer; Gegner werden gefährlicher.
- **Permadeath** – ein Leben, ein Lauf. Erreiche Ebene 8, um zu gewinnen.

## 🎮 Steuerung

| Taste | Aktion |
| --- | --- |
| `W` `A` `S` `D` / Pfeiltasten / `H` `J` `K` `L` | Bewegen & angreifen |
| `Q` | Heiltrank trinken |
| `>` `.` / Enter | Treppe hinabsteigen (auf `>` stehend) |
| `R` | Neustart (nach Spielende) |
| `Esc` | Beenden |

**Symbole:** `@` Held · `g` Kobold · `o` Ork · `T` Troll · `!` Heiltrank · `>` Treppe

## 🚀 Installation & Start

```bash
# Repository klonen
git clone <DEIN-REPO-URL>
cd dark-depths

# (empfohlen) virtuelle Umgebung
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Spiel starten
python main.py
```

> Benötigt **Python 3.10+**.

## 🧠 Wie die Gegner-KI funktioniert

Jeder Gegner ist ein kleiner Zustandsautomat ([`roguelike/ai.py`](roguelike/ai.py)):

```
        sieht Spieler                benachbart
 WANDER ────────────► CHASE ──────────────────► ANGRIFF
   ▲                    │
   │  Erinnerung        │ Spieler außer Sicht
   └────────────────────┘ (verfolgt letzte bekannte Position
        Erinnerung = 0      noch ENEMY_MEMORY_TURNS Runden)
```

- **Sichtprüfung:** Distanz + Bresenham-Sichtlinie (keine Wand dazwischen).
- **Verfolgung:** A*-Wegfindung ([`roguelike/pathfinding.py`](roguelike/pathfinding.py)) zur
  Spielerposition; blockierte Felder anderer Gegner werden umgangen.
- **Gedächtnis:** Verliert ein Gegner die Sicht, jagt er die zuletzt bekannte Position –
  du kannst also um Ecken entkommen, aber nicht sofort.

## 🗂️ Projektstruktur

```
dark-depths/
├── main.py                  # Einstiegspunkt
├── roguelike/
│   ├── config.py            # Größen, Farben, Tuning
│   ├── game.py              # Spielzustand, Rundenlogik, Hauptschleife
│   ├── game_map.py          # Tiles & Raster
│   ├── procgen.py           # prozedurale Dungeon-Generierung
│   ├── fov.py               # Field of View (Shadowcasting)
│   ├── pathfinding.py       # A*-Wegfindung
│   ├── ai.py                # Gegner-KI (Zustandsautomat)
│   ├── entities.py          # Spieler, Monster, Items
│   ├── combat.py            # Kampfauflösung
│   └── renderer.py          # Darstellung (pygame)
├── tests/                   # pytest-Suite (Logik ohne Fenster testbar)
├── requirements.txt
└── pyproject.toml
```

Die **Spiellogik ist bewusst von der Darstellung getrennt**: alle Kernmodule
(`procgen`, `fov`, `pathfinding`, `ai`, `combat`, `game`) kommen ohne pygame aus und
sind dadurch vollständig headless testbar.

## 🧪 Tests

```bash
pip install pytest
pytest
```

Die Suite deckt Dungeon-Generierung, Wegfindung, Sichtfeld, Kampf und KI-Verhalten ab.

## 📜 Lizenz

MIT – mach damit, was du willst.
