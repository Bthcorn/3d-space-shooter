"""Physics and collision detection system."""

from game.utils.math_utils import Vector3
from game.config import BOUNDING_SPHERE_SCALE


class BoundingSphere:
    """Bounding sphere for collision detection."""

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def intersects(self, other):
        distance = self.center.distance_to(other.center)
        return distance < (self.radius + other.radius)

    def contains_point(self, point):
        return self.center.distance_to(point) < self.radius


class CollisionSystem:
    """Handles collision detection and response."""

    @staticmethod
    def check_collision(entity1, entity2):
        s1 = BoundingSphere(entity1.position, entity1.get_radius())
        s2 = BoundingSphere(entity2.position, entity2.get_radius())
        return s1.intersects(s2)

    @staticmethod
    def check_collision_list(entity, entity_list):
        es = BoundingSphere(entity.position, entity.get_radius())
        for other in entity_list:
            if other == entity:
                continue
            os = BoundingSphere(other.position, other.get_radius())
            if es.intersects(os):
                return other
        return None

    @staticmethod
    def push_back(entity, direction, distance):
        push = direction.normalize() * -distance
        entity.position = entity.position + push

    @staticmethod
    def resolve_collision(entity1, entity2, push_distance):
        direction = entity1.position - entity2.position
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = Vector3(1, 0, 0)
        entity1.position = entity1.position + direction * push_distance

    @staticmethod
    def ray_sphere_intersection(ray_origin, ray_direction, sphere_center, sphere_radius):
        oc = ray_origin - sphere_center
        a = ray_direction.dot(ray_direction)
        b = 2.0 * oc.dot(ray_direction)
        c = oc.dot(oc) - sphere_radius * sphere_radius
        return (b * b - 4 * a * c) >= 0

    @staticmethod
    def check_projectile_collision(projectile, target):
        return CollisionSystem.check_collision(projectile, target)
