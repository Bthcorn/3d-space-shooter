# Space Shooter — Mini Game 2

A 3D first‑person space shooter built with **Python + Pygame + PyOpenGL** (fixed pipeline, no shaders).

For the full technical write‑up (materials, transparency, lighting model), see the
**[Technical Report](REPORT.md)**.

---

## Quick Start

### Setup with Python + pip

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies from requirements.txt
pip install -r requirements.txt

# (Optional) install the package so `space-shooter` script is available
pip install -e .
```

### Alternative: install with `uv`

```bash
# 1. Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Enter the project
cd 3d-space-shooter

# 3. Create virtualenv and install
uv venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 4. Install package (and dev extras if you like)
uv pip install -e .
uv pip install -e ".[dev]"
```

### Run the game

```bash
# Using installed script
space-shooter

# Or as a module
python -m game.main

# Or directly
python src/game/main.py
```

---

## Controls

- **W / S**: Move forward / backward
- **A / D**: Strafe left / right
- **Mouse**: Look around (first‑person)
- **Space**: Shoot laser
- **N**: Toggle night‑vision mode
- **T**: Toggle radar / detection HUD
- **R**: Restart (when game over)
- **ESC**: Pause / resume / quit

---

## Project Structure

```text
wireframe_space_shooter/
├── main.py              # Entry point
├── pyproject.toml       # Project + dependencies
├── README.md            # Quick start + structure (this file)
├── REPORT.md            # Technical report (materials, lighting, transparency)
└── src/game/
    ├── main.py          # Game loop & integration
    ├── config.py        # All configuration constants
    ├── engine/
    │   ├── renderer.py  # Solid OpenGL rendering + starfield
    │   ├── camera.py    # First‑person camera
    │   ├── physics.py   # Collision detection
    │   ├── lighting.py  # Day/night cycle + night‑vision
    │   └── materials.py # Material definitions & helpers
    ├── entities/
    │   ├── entity.py    # Base entity
    │   ├── player.py    # Player ship
    │   ├── enemy.py     # Enemies
    │   ├── meteorite.py # Meteorites
    │   ├── life_sphere.py
    │   ├── projectile.py
    │   └── explosion.py # Death explosion effect
    ├── utils/
    │   ├── math_utils.py
    │   └── models.py    # 3D model generators (solid + wireframe)
    └── ui/
        └── hud.py       # Heads‑up display overlay
```

---

## Dev Commands

From the project root with the virtualenv active:

```bash
# Run tests
pytest tests/ -v

# Format
black src/

# Lint
ruff check src/
```

If you want more background on the rendering and design decisions, open `REPORT.md`.
