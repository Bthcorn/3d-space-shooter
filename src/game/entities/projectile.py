"""Projectile / laser bolt entity."""

from game.entities.entity import Entity
from game.utils.models import create_laser_solid
from game.engine.materials import MATERIAL_LASER_GREEN, MATERIAL_LASER_RED
from game.config import (
    COLOR_PLAYER_LASER,
    COLOR_ENEMY_LASER,
    LASER_SPEED,
    LASER_LIFETIME,
    LASER_LENGTH,
)


class Projectile(Entity):
    """Laser projectile — emissive material so it glows regardless of light."""

    def __init__(self, position=None, direction=None, owner="player"):
        solid = create_laser_solid(length=LASER_LENGTH, radius=0.1)
        mat = MATERIAL_LASER_GREEN if owner == "player" else MATERIAL_LASER_RED

        super().__init__(position, model=None, solid_model=solid, material=mat)

        self.owner = owner
        self.direction = direction if direction else __import__('game.utils.math_utils', fromlist=['Vector3']).Vector3(0, 0, -1)
        self.velocity = self.direction * LASER_SPEED
        self.lifetime = LASER_LIFETIME
        self.radius = 0.3

        # Orient laser along velocity
        import math
        dx, dy, dz = self.direction.x, self.direction.y, self.direction.z
        self.rotation = [
            math.atan2(dy, (dx * dx + dz * dz) ** 0.5),
            math.atan2(dx, dz),
            0,
        ]

    def update(self, dt):
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.destroy()

    def is_player_projectile(self):
        return self.owner == "player"

    def is_enemy_projectile(self):
        return self.owner == "enemy"

    def get_color(self):
        return COLOR_PLAYER_LASER if self.owner == "player" else COLOR_ENEMY_LASER

    def __repr__(self):
        return f"Projectile(owner={self.owner}, pos={self.position})"
