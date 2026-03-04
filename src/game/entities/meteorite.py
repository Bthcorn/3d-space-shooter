"""Meteorite obstacle entity."""

import random
import math
from game.entities.entity import Entity
from game.utils.models import create_meteorite_solid
from game.engine.materials import MATERIAL_MATTE_GRAY
from game.config import (
    COLOR_METEORITE,
    METEORITE_MIN_SIZE,
    METEORITE_MAX_SIZE,
)


class Meteorite(Entity):
    """Indestructible rotating meteorite obstacle."""

    def __init__(self, position=None):
        self.size = random.uniform(METEORITE_MIN_SIZE, METEORITE_MAX_SIZE)
        solid = create_meteorite_solid(size=self.size * 0.5)

        super().__init__(position, model=None, solid_model=solid,
                         material=MATERIAL_MATTE_GRAY)

        self.radius = self.size
        self.scale = (1.0, 1.0, 1.0)

        # Random slow rotation
        self.rot_speed = [
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
            random.uniform(-0.5, 0.5),
        ]

    def update(self, dt):
        super().update(dt)
        self.rotation[0] += self.rot_speed[0] * dt
        self.rotation[1] += self.rot_speed[1] * dt
        self.rotation[2] += self.rot_speed[2] * dt

    def get_color(self):
        return COLOR_METEORITE

    def __repr__(self):
        return f"Meteorite(pos={self.position}, size={self.size:.1f})"
