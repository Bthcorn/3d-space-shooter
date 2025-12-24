# Wireframe Space Shooter

A 3D wireframe first-person space shooter game built with Python, Pygame, and PyOpenGL.

## Features

- **3D Wireframe Graphics**: All objects rendered as wireframe models
- **First-Person Action**: Immersive cockpit view
- **Multiple Object Types**: 
  - Player spaceship (controllable)
  - Enemy spaceships (AI-controlled)
  - Meteorites (obstacles)
  - Life spheres (power-ups)
  - Laser projectiles
- **Transformations**: Translation, rotation, and scaling
- **Collision Detection**: Advanced 3D collision system
- **HUD**: Real-time display of lives and score
- **Enemy AI**: Enemies shoot projectiles at the player

## Game Mechanics

### Player Controls
- **W/S**: Move forward/backward
- **A/D**: Strafe left/right
- **Mouse**: Look around
- **Space**: Shoot laser
- **ESC**: Pause/Menu

### Scoring System
- Destroy light spaceship: +1 point
- Hit meteorite: -1 point (pushes back)
- Collect life sphere: +1 life
- Hit by enemy fire: -1 life

### Enemy Types
- **Light Spaceship**: Fast moving, 1 HP, awards 1 point when destroyed

### Obstacles
- **Meteorite**: Indestructible, blocks lasers, causes damage on collision

### Power-ups
- **Life Sphere**: Grants +1 life when collected or shot

## Installation

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd wireframe_space_shooter

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# For development dependencies
uv pip install -e ".[dev]"
```

### Traditional pip

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Running the Game

```bash
# If installed with scripts
space-shooter

# Or directly
python -m game.main
```

## Project Structure

```
wireframe_space_shooter/
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # This file
├── src/
│   └── game/
│       ├── __init__.py
│       ├── main.py         # Entry point
│       ├── config.py       # Game configuration
│       ├── engine/         # Core engine components
│       │   ├── __init__.py
│       │   ├── renderer.py # OpenGL rendering
│       │   ├── camera.py   # Camera control
│       │   └── physics.py  # Collision detection
│       ├── entities/       # Game objects
│       │   ├── __init__.py
│       │   ├── player.py
│       │   ├── enemy.py
│       │   ├── meteorite.py
│       │   ├── life_sphere.py
│       │   └── projectile.py
│       ├── utils/          # Utilities
│       │   ├── __init__.py
│       │   ├── math_utils.py
│       │   └── models.py   # 3D model definitions
│       └── ui/             # UI components
│           ├── __init__.py
│           └── hud.py      # Heads-up display
├── tests/                  # Unit tests
└── assets/                 # Game assets (textures, sounds)
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
ruff check src/
```

## Learning Objectives

This project demonstrates:
1. **3D Graphics Programming**: OpenGL wireframe rendering
2. **Object-Oriented Design**: Entity system architecture
3. **Game Physics**: Collision detection and response
4. **Camera Systems**: First-person camera control
5. **Game Logic**: Enemy AI, scoring, lives system
6. **Matrix Transformations**: Translation, rotation, scaling

## License

Educational project for learning 3D game development.
