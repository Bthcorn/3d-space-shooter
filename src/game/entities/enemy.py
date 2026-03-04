"""Enemy spaceship entity."""

import math
import random as _random
from game.entities.entity import Entity
from game.utils.models import EnemyModelFactory
from game.engine.materials import ENEMY_MATERIAL_POOL
from game.config import (
    COLOR_ENEMY,
    ENEMY_SPEED,
    ENEMY_HEALTH,
    ENEMY_POINTS,
    ENEMY_SHOOT_INTERVAL,
    ENEMY_SHOOT_RANGE,
)


class Enemy(Entity):
    """AI-controlled enemy spaceship."""

    def __init__(self, position=None, model_builder=None):
        # Wireframe model (legacy)
        if model_builder:
            wire_model = model_builder()
        else:
            wire_model = EnemyModelFactory.create_standard()

        # Solid model for lit rendering
        solid = EnemyModelFactory.get_random_solid()

        # Random glossy material per enemy
        mat = _random.choice(ENEMY_MATERIAL_POOL)

        super().__init__(position, wire_model, solid_model=solid,
                         material=mat)

        self.radius = 2.5
        self.health = ENEMY_HEALTH
        self.points = ENEMY_POINTS
        self.speed = ENEMY_SPEED
        self.shoot_timer = 0.0

    def update(self, dt, target_pos=None):
        super().update(dt)

        if target_pos:
            # Move toward target
            direction = target_pos - self.position
            dist = direction.length()
            if dist > 5.0:
                direction = direction.normalize()
                self.velocity = direction * self.speed
                # Face the target
                self.rotation[1] = math.atan2(direction.x, direction.z)
            else:
                self.velocity.x = 0
                self.velocity.y = 0
                self.velocity.z = 0

        self.shoot_timer += dt

    def can_shoot(self, target_pos):
        if self.shoot_timer >= ENEMY_SHOOT_INTERVAL:
            dist = self.position.distance_to(target_pos)
            if dist <= ENEMY_SHOOT_RANGE:
                self.shoot_timer = 0.0
                return True
        return False

    def get_shoot_direction(self, target_pos):
        direction = target_pos - self.position
        return direction.normalize()

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.destroy()

    def get_points(self):
        return self.points

    def get_color(self):
        return COLOR_ENEMY

    def __repr__(self):
        return f"Enemy(pos={self.position}, hp={self.health})"
