"""Simple tests for game components"""

import pytest
from game.utils.math_utils import Vector3, rotation_matrix_y
from game.entities.player import Player
from game.entities.enemy import Enemy
from game.engine.physics import CollisionSystem
import numpy as np


class TestVector3:
    """Test Vector3 class"""

    def test_vector_creation(self):
        v = Vector3(1, 2, 3)
        assert v.x == 1
        assert v.y == 2
        assert v.z == 3

    def test_vector_addition(self):
        v1 = Vector3(1, 2, 3)
        v2 = Vector3(4, 5, 6)
        v3 = v1 + v2
        assert v3.x == 5
        assert v3.y == 7
        assert v3.z == 9

    def test_vector_length(self):
        v = Vector3(3, 4, 0)
        assert v.length() == 5.0

    def test_vector_normalize(self):
        v = Vector3(3, 4, 0)
        n = v.normalize()
        assert abs(n.length() - 1.0) < 0.001


class TestEntities:
    """Test game entities"""

    def test_player_creation(self):
        player = Player()
        assert player.lives == 3
        assert player.is_alive()

    def test_player_damage(self):
        player = Player()
        player.take_damage()
        assert player.lives == 2
        assert player.is_alive()

        player.take_damage()
        player.take_damage()
        assert player.lives == 0
        assert not player.is_alive()

    def test_enemy_creation(self):
        enemy = Enemy()
        assert enemy.health == 1
        assert enemy.is_alive()


class TestCollision:
    """Test collision system"""

    def test_collision_detection(self):
        player = Player(Vector3(0, 0, 0))
        enemy = Enemy(Vector3(2, 0, 0))

        # Should collide (within combined radius)
        collision = CollisionSystem.check_collision(player, enemy)
        assert collision

    def test_no_collision(self):
        player = Player(Vector3(0, 0, 0))
        enemy = Enemy(Vector3(100, 0, 0))

        # Should not collide (too far apart)
        collision = CollisionSystem.check_collision(player, enemy)
        assert not collision


class TestTransformations:
    """Test transformation matrices"""

    def test_rotation_matrix(self):
        # Test 90 degree rotation around Y axis
        matrix = rotation_matrix_y(np.pi / 2)
        assert matrix.shape == (4, 4)
        # After 90° rotation around Y, X becomes -Z and Z becomes X
        # Check approximate equality due to floating point
        assert abs(matrix[0, 0]) < 0.001  # cos(90°) ≈ 0
        assert abs(matrix[0, 2] - 1.0) < 0.001  # sin(90°) ≈ 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
