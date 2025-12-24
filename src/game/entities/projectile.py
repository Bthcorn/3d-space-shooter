"""Projectile entity for lasers"""

from game.entities.entity import Entity
from game.utils.models import create_laser
from game.utils.math_utils import Vector3
from game.config import (
    COLOR_PLAYER_LASER,
    COLOR_ENEMY_LASER,
    LASER_SPEED,
    LASER_LIFETIME,
    LASER_LENGTH,
)


class Projectile(Entity):
    """Laser projectile"""

    def __init__(self, position, direction, owner_type="player"):
        """
        Initialize projectile

        Args:
            position: Starting position (Vector3)
            direction: Firing direction (Vector3, normalized)
            owner_type: "player" or "enemy"
        """
        model = create_laser(LASER_LENGTH)
        super().__init__(position, model)

        self.owner_type = owner_type
        self.direction = direction.normalize()
        self.velocity = self.direction * LASER_SPEED
        self.radius = 0.3  # Small collision radius
        self.lifetime = LASER_LIFETIME
        self.age = 0.0

        # Orient laser in direction of travel
        self._set_rotation_from_direction()

    def update(self, dt):
        """Update projectile state"""
        super().update(dt)

        self.age += dt
        if self.age >= self.lifetime:
            self.destroy()

    def _set_rotation_from_direction(self):
        """Set rotation to align with direction vector"""
        import math

        # Calculate yaw and pitch from direction
        # This aligns the laser with its travel direction
        if self.direction.length() > 0:
            # Yaw (rotation around Y axis)
            yaw = math.atan2(self.direction.x, self.direction.z)

            # Pitch (rotation around X axis)
            xz_length = math.sqrt(self.direction.x**2 + self.direction.z**2)
            pitch = math.atan2(self.direction.y, xz_length)

            self.rotation = [pitch, yaw, 0]

    def is_player_projectile(self):
        """Check if this is a player projectile"""
        return self.owner_type == "player"

    def is_enemy_projectile(self):
        """Check if this is an enemy projectile"""
        return self.owner_type == "enemy"

    def get_color(self):
        """Get projectile color based on owner"""
        if self.owner_type == "player":
            return COLOR_PLAYER_LASER
        else:
            return COLOR_ENEMY_LASER

    def __repr__(self):
        return f"Projectile(pos={self.position}, owner={self.owner_type})"
