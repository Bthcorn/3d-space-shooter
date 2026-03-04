"""Explosion effect entity for dying enemies."""

from game.entities.entity import Entity
from game.utils.models import create_sphere
from game.engine.materials import MATERIAL_EXPLOSION
from game.utils.math_utils import clamp


class Explosion(Entity):
    """Short-lived expanding explosion sphere."""

    def __init__(self, position=None, duration=0.6, start_scale=0.5, end_scale=4.0):
        solid = create_sphere(radius=1.0, slices=10, stacks=6)
        super().__init__(position, model=None, solid_model=solid, material=MATERIAL_EXPLOSION)

        self.duration = duration
        self.age = 0.0
        self.start_scale = start_scale
        self.end_scale = end_scale

        self.scale = (start_scale, start_scale, start_scale)
        # Explosions do not collide, so radius is only for visuals if needed
        self.radius = end_scale

    def update(self, dt):
        """Expand and fade over time, then disappear."""
        super().update(dt)
        self.age += dt

        t = clamp(self.age / self.duration, 0.0, 1.0)
        s = self.start_scale + (self.end_scale - self.start_scale) * t
        self.scale = (s, s, s)

        if self.age >= self.duration:
            self.destroy()
