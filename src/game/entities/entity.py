"""Base entity class for all game objects"""

from game.utils.math_utils import Vector3


class Entity:
    """Base class for all game entities"""

    def __init__(self, position=None, model=None):
        """
        Args:
            position: Starting position (Vector3)
            model: WireframeModel for rendering
        """
        self.position = position if position else Vector3(0, 0, 0)
        self.model = model
        self.velocity = Vector3(0, 0, 0)
        self.rotation = [0.0, 0.0, 0.0]  # Rotation in radians [x, y, z]
        self.scale = (1.0, 1.0, 1.0)
        self.alive = True
        self.radius = 1.0  # For collision detection

    def update(self, dt):
        """
        Update entity state

        Args:
            dt: Delta time in seconds
        """
        # Update position based on velocity
        self.position = self.position + self.velocity * dt

    def get_radius(self):
        """Get collision radius"""
        return self.radius

    def set_position(self, x, y, z):
        """Set entity position"""
        self.position = Vector3(x, y, z)

    def set_velocity(self, x, y, z):
        """Set entity velocity"""
        self.velocity = Vector3(x, y, z)

    def set_rotation(self, rx, ry, rz):
        """Set entity rotation in radians"""
        self.rotation = [rx, ry, rz]

    def rotate(self, drx, dry, drz):
        """Add to current rotation"""
        self.rotation[0] += drx
        self.rotation[1] += dry
        self.rotation[2] += drz

    def set_scale(self, sx, sy, sz):
        """Set entity scale"""
        self.scale = (sx, sy, sz)

    def destroy(self):
        """Mark entity for removal"""
        self.alive = False

    def is_alive(self):
        """Check if entity is alive"""
        return self.alive

    def get_color(self):
        """Get entity render color - override in subclasses"""
        return (1.0, 1.0, 1.0)

    def __repr__(self):
        return f"{self.__class__.__name__}(pos={self.position}, alive={self.alive})"
