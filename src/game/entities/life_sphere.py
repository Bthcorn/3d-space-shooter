"""Life sphere power-up entity"""

from game.entities.entity import Entity
from game.utils.models import create_life_sphere
from game.config import (
    COLOR_LIFE_SPHERE,
    LIFE_SPHERE_SIZE,
    LIFE_SPHERE_ROTATION_SPEED,
)


class LifeSphere(Entity):
    """Life power-up sphere"""

    def __init__(self, position=None):
        """Initialize life sphere"""
        model = create_life_sphere(LIFE_SPHERE_SIZE)
        super().__init__(position, model)

        self.radius = LIFE_SPHERE_SIZE
        self.scale = (LIFE_SPHERE_SIZE, LIFE_SPHERE_SIZE, LIFE_SPHERE_SIZE)
        self.collected = False

    def update(self, dt):
        """Update life sphere state"""
        super().update(dt)

        # Rotate for visual effect
        self.rotate(
            dt * LIFE_SPHERE_ROTATION_SPEED,
            dt * LIFE_SPHERE_ROTATION_SPEED * 1.5,
            dt * LIFE_SPHERE_ROTATION_SPEED * 0.8,
        )

        # Gentle bobbing motion
        import math

        self.position.y += math.sin(pygame.time.get_ticks() * 0.002) * 0.01

    def collect(self):
        """Mark sphere as collected"""
        self.collected = True
        self.destroy()

    def is_collected(self):
        """Check if sphere was collected"""
        return self.collected

    def get_color(self):
        """Get life sphere color"""
        return COLOR_LIFE_SPHERE

    def __repr__(self):
        return f"LifeSphere(pos={self.position})"


# Need to import pygame for the time function
import pygame
