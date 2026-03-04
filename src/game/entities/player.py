"""Player spaceship entity."""

from game.entities.entity import Entity
from game.utils.models import create_player_ship, create_player_ship_solid
from game.engine.materials import MATERIAL_METAL_SILVER
from game.config import (
    COLOR_PLAYER,
    PLAYER_STARTING_LIVES,
    PLAYER_SHOOT_COOLDOWN,
)


class Player(Entity):
    """Player controlled spaceship."""

    def __init__(self, position=None):
        model = create_player_ship()
        solid = create_player_ship_solid()
        super().__init__(position, model, solid_model=solid,
                         material=MATERIAL_METAL_SILVER)

        self.radius = 2.0
        self.lives = PLAYER_STARTING_LIVES
        self.shoot_cooldown = 0.0
        self.damage_flash_timer = 0.0
        self.can_shoot = True

    def update(self, dt):
        super().update(dt)
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            if self.shoot_cooldown <= 0:
                self.can_shoot = True
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt

    def shoot(self):
        if self.can_shoot:
            self.can_shoot = False
            self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
            return True
        return False

    def take_damage(self):
        self.lives -= 1
        self.damage_flash_timer = 0.5
        if self.lives <= 0:
            self.destroy()

    def add_life(self):
        self.lives += 1

    def get_lives(self):
        return self.lives

    def get_color(self):
        return COLOR_PLAYER

    def __repr__(self):
        return f"Player(pos={self.position}, lives={self.lives})"
