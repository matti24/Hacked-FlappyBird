"""Startpunkt für NeuroFlap.

Aufruf:  python main.py
Läuft nativ (Desktop) und im Browser via pygbag (WebAssembly).
"""

import asyncio

import pygame  # noqa: F401 - Top-Level-Import, damit pygbag pygame vorlädt

from neuroflap.simulation import main

asyncio.run(main())
