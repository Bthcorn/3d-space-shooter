"""Game configuration constants"""

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Wireframe Space Shooter"
FPS = 60

# OpenGL settings
FOV = 70.0  # Field of view
NEAR_PLANE = 0.1
FAR_PLANE = 1000.0

# Player settings
PLAYER_SPEED = 30.0  # Units per second
PLAYER_STRAFE_SPEED = 20.0  # Units per second
PLAYER_MOUSE_SENSITIVITY = 0.2
PLAYER_STARTING_LIVES = 3
PLAYER_SHOOT_COOLDOWN = 0.3  # seconds

# Player ship view (cockpit perspective)
PLAYER_SHIP_OFFSET_FORWARD = 0.1  # Distance in front of camera (POSITIVE = in front)
PLAYER_SHIP_OFFSET_DOWN = 0.0  # Distance below camera (negative = down)
PLAYER_SHIP_OFFSET_RIGHT = 0.0  # Horizontal offset (0 = centered)
PLAYER_SHIP_SCALE = 1.2  # Visual scale (increased for better visibility)

# Player ship animation (dynamic movement response)
SHIP_ROLL_SENSITIVITY = 1.0  # How much ship banks when turning (0-5)
SHIP_PITCH_SENSITIVITY = 0.5  # How much ship pitches when looking up/down (0-5)
SHIP_ANIMATION_DAMPING = 10.0  # Smoothness of animations (higher = smoother, 1-20)
MAX_SHIP_ROLL = 15.0  # Maximum roll angle in degrees
MAX_SHIP_PITCH_OFFSET = 8.0  # Maximum pitch offset in degrees

# Camera settings
CAMERA_YAW_LIMIT = 89.0  # Prevent camera flip

# Enemy settings
ENEMY_SPEED = 15.0  # Units per second
ENEMY_SPAWN_DISTANCE = 100.0
ENEMY_SPAWN_INTERVAL = 3.0  # seconds
ENEMY_SHOOT_INTERVAL = 2.0  # seconds
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
LIFE_SPHERE_SPAWN_INTERVAL = 10.0  # seconds
LIFE_SPHERE_ROTATION_SPEED = 2.0

# Projectile settings
LASER_SPEED = 80.0  # Units per second
LASER_LIFETIME = 5.0  # seconds
LASER_LENGTH = 2.0

# Physics
COLLISION_PUSH_BACK = 5.0
BOUNDING_SPHERE_SCALE = 1.2  # Multiplier for collision detection

# World bounds
WORLD_SIZE = 200.0

# Colors (RGB)
COLOR_PLAYER = (0.0, 1.0, 0.0)  # Green
COLOR_ENEMY = (1.0, 0.0, 0.0)  # Red
COLOR_METEORITE = (0.5, 0.5, 0.5)  # Gray
COLOR_LIFE_SPHERE = (0.0, 1.0, 1.0)  # Cyan
COLOR_PLAYER_LASER = (0.0, 1.0, 0.0)  # Green
COLOR_ENEMY_LASER = (1.0, 0.0, 0.0)  # Red
COLOR_HUD = (1.0, 1.0, 1.0)  # White
