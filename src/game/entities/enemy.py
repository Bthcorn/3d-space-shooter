"""Enemy spaceship entity"""

import random
from game.entities.entity import Entity
from game.utils.models import EnemyModelFactory
from game.utils.math_utils import Vector3
from game.config import (
    COLOR_ENEMY,
    ENEMY_SPEED,
    ENEMY_HEALTH,
    ENEMY_POINTS,
    ENEMY_SHOOT_INTERVAL,
    ENEMY_SHOOT_RANGE,
)


class Enemy(Entity):
    """AI-controlled enemy spaceship"""

    def __init__(self, position=None, model_factory=None):
        """Initialize enemy"""
        if model_factory:
            model = model_factory()
        else:
            model = EnemyModelFactory.create_standard()
        super().__init__(position, model)

        self.radius = 1.5  # Collision radius
        self.health = ENEMY_HEALTH
        self.points = ENEMY_POINTS
        self.shoot_timer = random.uniform(0, ENEMY_SHOOT_INTERVAL)
        self.target_position = None  # Will track player

    def update(self, dt, player_position=None):
        """
        Update enemy state

        Args:
            dt: Delta time
            player_position: Player's position for AI
        """
        super().update(dt)

        # AI: Move toward player
        if player_position:
            self._move_toward_target(player_position, dt)

        # Update shoot timer
        self.shoot_timer -= dt

        # Rotate for visual effect
        self.rotate(0, dt * 0.5, 0)

    def _move_toward_target(self, target_pos, dt):
        """Move enemy toward target position"""
        direction = target_pos - self.position
        distance = direction.length()

        if distance > 10.0:  # Keep some distance
            direction = direction.normalize()
            self.velocity = direction * ENEMY_SPEED
        else:
            self.velocity = Vector3(0, 0, 0)

    def can_shoot(self, player_position):
        """
        Check if enemy can shoot at player

        Args:
            player_position: Player's position

        Returns:
            bool: True if enemy can shoot
        """
        if self.shoot_timer <= 0:
            distance = self.position.distance_to(player_position)
            if distance < ENEMY_SHOOT_RANGE:
                self.shoot_timer = ENEMY_SHOOT_INTERVAL
                return True
        return False

    def get_shoot_direction(self, player_position):
        """
        Get direction to shoot at player

        Args:
            player_position: Player's position

        Returns:
            Vector3: Normalized direction vector
        """
        direction = player_position - self.position
        return direction.normalize()

    def take_damage(self, damage=1):
        """
        Take damage

        Args:
            damage: Amount of damage
        """
        self.health -= damage
        if self.health <= 0:
            self.destroy()

    def get_points(self):
        """Get points awarded for destroying this enemy"""
        return self.points

    def get_color(self):
        """Get enemy color"""
        return COLOR_ENEMY

    def __repr__(self):
        return f"Enemy(pos={self.position}, health={self.health})"
