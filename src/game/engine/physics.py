"""Physics and collision detection system"""

from game.utils.math_utils import Vector3
from game.config import BOUNDING_SPHERE_SCALE


class BoundingSphere:
    """Bounding sphere for collision detection"""

    def __init__(self, center, radius):
        """
        Args:
            center: Vector3 center position
            radius: Sphere radius
        """
        self.center = center
        self.radius = radius

    def intersects(self, other):
        """Check if this sphere intersects another sphere"""
        distance = self.center.distance_to(other.center)
        return distance < (self.radius + other.radius)

    def contains_point(self, point):
        """Check if a point is inside this sphere"""
        distance = self.center.distance_to(point)
        return distance < self.radius


class CollisionSystem:
    """Handles collision detection and response"""

    @staticmethod
    def check_collision(entity1, entity2):
        """
        Check if two entities collide using bounding spheres

        Args:
            entity1, entity2: Game entities with position and get_radius() method

        Returns:
            bool: True if collision detected
        """
        sphere1 = BoundingSphere(entity1.position, entity1.get_radius())
        sphere2 = BoundingSphere(entity2.position, entity2.get_radius())
        return sphere1.intersects(sphere2)

    @staticmethod
    def check_collision_list(entity, entity_list):
        """
        Check if entity collides with any entity in list

        Args:
            entity: Single entity
            entity_list: List of entities to check

        Returns:
            Colliding entity or None
        """
        entity_sphere = BoundingSphere(entity.position, entity.get_radius())

        for other in entity_list:
            if other == entity:
                continue

            other_sphere = BoundingSphere(other.position, other.get_radius())
            if entity_sphere.intersects(other_sphere):
                return other

        return None

    @staticmethod
    def push_back(entity, direction, distance):
        """
        Push entity back in opposite direction

        Args:
            entity: Entity to push
            direction: Push direction (Vector3)
            distance: Push distance
        """
        push_vector = direction.normalize() * -distance
        entity.position = entity.position + push_vector

    @staticmethod
    def resolve_collision(entity1, entity2, push_distance):
        """
        Resolve collision by pushing entities apart

        Args:
            entity1, entity2: Colliding entities
            push_distance: How far to push them apart
        """
        # Calculate direction from entity2 to entity1
        direction = entity1.position - entity2.position
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            # If positions are identical, push in random direction
            direction = Vector3(1, 0, 0)

        # Push entity1 back
        entity1.position = entity1.position + direction * push_distance

    @staticmethod
    def ray_sphere_intersection(ray_origin, ray_direction, sphere_center, sphere_radius):
        """
        Check if a ray intersects a sphere

        Args:
            ray_origin: Ray start position (Vector3)
            ray_direction: Ray direction (Vector3, normalized)
            sphere_center: Sphere center (Vector3)
            sphere_radius: Sphere radius

        Returns:
            bool: True if ray intersects sphere
        """
        # Vector from ray origin to sphere center
        oc = ray_origin - sphere_center

        # Quadratic equation coefficients
        a = ray_direction.dot(ray_direction)
        b = 2.0 * oc.dot(ray_direction)
        c = oc.dot(oc) - sphere_radius * sphere_radius

        # Discriminant
        discriminant = b * b - 4 * a * c

        return discriminant >= 0

    @staticmethod
    def check_projectile_collision(projectile, target):
        """
        Check if a projectile hits a target

        Args:
            projectile: Projectile entity
            target: Target entity

        Returns:
            bool: True if hit
        """
        return CollisionSystem.check_collision(projectile, target)
