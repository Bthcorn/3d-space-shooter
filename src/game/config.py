"""Game configuration constants"""

import math

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Space Shooter — Mini Game 2"
FPS = 60

# OpenGL settings
FOV = 70.0
NEAR_PLANE = 0.1
FAR_PLANE = 1000.0

# Player settings
PLAYER_SPEED = 30.0
PLAYER_STRAFE_SPEED = 20.0
PLAYER_MOUSE_SENSITIVITY = 0.2
PLAYER_STARTING_LIVES = 3
PLAYER_SHOOT_COOLDOWN = 0.3

# Player ship view
PLAYER_SHIP_OFFSET_FORWARD = 0.1
PLAYER_SHIP_OFFSET_DOWN = 0.0
PLAYER_SHIP_OFFSET_RIGHT = 0.0
PLAYER_SHIP_SCALE = 1.2

# Player ship animation
SHIP_ROLL_SENSITIVITY = 1.0
SHIP_PITCH_SENSITIVITY = 0.5
SHIP_ANIMATION_DAMPING = 10.0
MAX_SHIP_ROLL = 15.0
MAX_SHIP_PITCH_OFFSET = 8.0

# Camera settings
CAMERA_YAW_LIMIT = 89.0

# Enemy settings
ENEMY_SPEED = 15.0
ENEMY_SPAWN_DISTANCE = 100.0
ENEMY_SPAWN_INTERVAL = 3.0
ENEMY_SHOOT_INTERVAL = 2.0
ENEMY_SHOOT_RANGE = 50.0
ENEMY_HEALTH = 1
ENEMY_POINTS = 1

# Meteorite settings
METEORITE_MIN_SIZE = 2.0
METEORITE_MAX_SIZE = 5.0
METEORITE_SPAWN_DISTANCE = 80.0
METEORITE_COUNT = 10
METEORITE_COLLISION_PENALTY = -1

# Life sphere settings
LIFE_SPHERE_SIZE = 1.5
LIFE_SPHERE_SPAWN_DISTANCE = 70.0
LIFE_SPHERE_SPAWN_INTERVAL = 10.0
LIFE_SPHERE_ROTATION_SPEED = 2.0

# Projectile settings
LASER_SPEED = 80.0
LASER_LIFETIME = 5.0
LASER_LENGTH = 2.0

# Physics
COLLISION_PUSH_BACK = 5.0
BOUNDING_SPHERE_SCALE = 1.2

# World bounds
WORLD_SIZE = 200.0

# Colors (RGB)
COLOR_PLAYER = (0.0, 1.0, 0.0)
COLOR_ENEMY = (1.0, 0.0, 0.0)
COLOR_METEORITE = (0.5, 0.5, 0.5)
COLOR_LIFE_SPHERE = (0.0, 1.0, 1.0)
COLOR_PLAYER_LASER = (0.0, 1.0, 0.0)
COLOR_ENEMY_LASER = (1.0, 0.0, 0.0)
COLOR_HUD = (1.0, 1.0, 1.0)

# ============================================================
# MINI GAME 2: Lighting, Materials, Day/Night, Flashlight
# ============================================================

# ── Day / Night cycle ────────────────────────────────────────────────────────
# A single smooth parameter  t = (1 − cos(2π·time)) / 2  drives all three
# visual effects below.  t=0 → midnight,  t=1 → noon.

DAY_NIGHT_CYCLE_SPEED = 0.03  # time units per second  (full cycle ≈ 33 s)

# ── Visual Parameter 1 · sky / background  glClearColor ─────────────────────
# Both endpoints are dark — space has no atmosphere so the sky is always black.
# The subtle shift from deep-navy (noon) to near-void (midnight) keeps the
# cycle visible without introducing any non-space colour.
SKY_DAY = (0.02, 0.02, 0.08, 1.0)  # very dark navy — sun is up
SKY_NIGHT = (0.00, 0.00, 0.02, 1.0)  # near-black void — midnight

# Starfield
STAR_COUNT = 600

# ── Visual Parameter 2 · GL_LIGHT0 colour  (sun ↔ moon, same light) ─────────
# Space sunlight is a sharp, nearly neutral-white directional light with
# minimal ambient component — no atmosphere means no scattered fill light.
SUN_DIFFUSE = (1.00, 0.98, 0.92, 1.0)  # bright, nearly white sunlight
SUN_SPECULAR = (1.00, 1.00, 1.00, 1.0)  # pure white specular highlight
SUN_AMBIENT = (0.04, 0.04, 0.06, 1.0)  # tiny cool ambient (no atmosphere)

MOON_DIFFUSE = (0.08, 0.09, 0.20, 1.0)  # faint cool moonlight
MOON_SPECULAR = (0.10, 0.10, 0.22, 1.0)
MOON_AMBIENT = (0.01, 0.01, 0.04, 1.0)  # nearly nothing

# ── Visual Parameter 3 · scene brightness  GL_LIGHT_MODEL_AMBIENT ───────────
# Kept deliberately low: in space even "daytime" has no atmospheric scatter.
# The cycle is still clearly visible — noon is ~5× brighter than midnight.
GLOBAL_AMBIENT_DAY = (0.10, 0.10, 0.14, 1.0)  # dim cool fill at noon
GLOBAL_AMBIENT_NIGHT = (0.02, 0.02, 0.05, 1.0)  # near-black at midnight

# Light-source orbit geometry
LIGHT_ORBIT_RADIUS = 200.0
LIGHT_HEIGHT = 150.0

# Night-vision boost
NIGHT_VISION_AMBIENT = (0.1, 0.4, 0.1, 1.0)
