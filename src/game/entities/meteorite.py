"""Meteorite obstacle entity"""

import random
from game.entities.entity import Entity
from game.utils.models import create_meteorite
from game.config import (
    COLOR_METEORITE,
    METEORITE_MIN_SIZE,
    METEORITE_MAX_SIZE,
)


class Meteorite(Entity):
    """Indestructible meteorite obstacle"""

    def __init__(self, position=None, size=None):
        """
        Initialize meteorite

        Args:
            position: Starting position
            size: Meteorite size (random if not specified)
        """
        if size is None:
            size = random.uniform(METEORITE_MIN_SIZE, METEORITE_MAX_SIZE)

        model = create_meteorite(size)
        super().__init__(position, model)

        self.size = size
        self.radius = size * 1.2  # Collision radius
        self.scale = (size, size, size)

        # Random slow rotation
        self.rotation_speed = [
            random.uniform(-0.2, 0.2),
            random.uniform(-0.2, 0.2),
            random.uniform(-0.2, 0.2),
        ]

        # Optional: slow drift velocity
        self.velocity.x = random.uniform(-0.05, 0.05)
        self.velocity.y = random.uniform(-0.05, 0.05)
        self.velocity.z = random.uniform(-0.05, 0.05)

    def update(self, dt):
        """Update meteorite state"""
        super().update(dt)

        # Rotate
        self.rotate(
            self.rotation_speed[0] * dt,
            self.rotation_speed[1] * dt,
            self.rotation_speed[2] * dt,
        )

    def is_indestructible(self):
        """Meteorites are indestructible"""
        return True

    def get_color(self):
        """Get meteorite color"""
        return COLOR_METEORITE

    def __repr__(self):
        return f"Meteorite(pos={self.position}, size={self.size:.1f})"
