"""Player spaceship entity"""

from game.entities.entity import Entity
from game.utils.models import create_player_ship
from game.config import (
    COLOR_PLAYER,
    PLAYER_STARTING_LIVES,
    PLAYER_SHOOT_COOLDOWN,
)


class Player(Entity):
    """Player controlled spaceship"""

    def __init__(self, position=None):
        """Initialize player"""
        model = create_player_ship()
        super().__init__(position, model)

        self.radius = 2.0  # Collision radius
        self.lives = PLAYER_STARTING_LIVES
        self.shoot_cooldown = 0.0
        self.damage_flash_timer = 0.0
        self.can_shoot = True

    def update(self, dt):
        """Update player state"""
        super().update(dt)

        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            if self.shoot_cooldown <= 0:
                self.can_shoot = True

        # Update damage flash
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt

    def shoot(self):
        """
        Attempt to shoot

        Returns:
            bool: True if shot was fired
        """
        if self.can_shoot:
            self.can_shoot = False
            self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
            return True
        return False

    def take_damage(self):
        """Take damage (lose a life)"""
        self.lives -= 1
        self.damage_flash_timer = 0.5  # Flash for 0.5 seconds
        if self.lives <= 0:
            self.destroy()

    def add_life(self):
        """Gain a life"""
        self.lives += 1

    def get_lives(self):
        """Get current lives"""
        return self.lives

    def get_color(self):
        """Get player color"""
        return COLOR_PLAYER

    def __repr__(self):
        return f"Player(pos={self.position}, lives={self.lives})"
