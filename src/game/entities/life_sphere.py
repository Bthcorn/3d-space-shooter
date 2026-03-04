"""Life sphere power-up entity — uses transparent material."""

from game.entities.entity import Entity
from game.utils.models import create_life_sphere_solid
from game.engine.materials import MATERIAL_LIFE_SPHERE
from game.config import (
    COLOR_LIFE_SPHERE,
    LIFE_SPHERE_SIZE,
    LIFE_SPHERE_ROTATION_SPEED,
)


class LifeSphere(Entity):
    """Collectible life sphere with transparent / glowing material."""

    def __init__(self, position=None):
        solid = create_life_sphere_solid(radius=LIFE_SPHERE_SIZE)
        super().__init__(position, model=None, solid_model=solid,
                         material=MATERIAL_LIFE_SPHERE)

        self.radius = LIFE_SPHERE_SIZE
        self.rot_speed = LIFE_SPHERE_ROTATION_SPEED

    def update(self, dt):
        super().update(dt)
        self.rotation[1] += self.rot_speed * dt

    def collect(self):
        """Mark as collected."""
        self.destroy()

    def get_color(self):
        return COLOR_LIFE_SPHERE

    def __repr__(self):
        return f"LifeSphere(pos={self.position})"
