"""Base entity class for all game objects."""

from game.utils.math_utils import Vector3


class Entity:
    """Base class for all game entities."""

    def __init__(self, position=None, model=None, solid_model=None, material=None):
        """
        Args:
            position: Starting position (Vector3)
            model: WireframeModel for legacy rendering
            solid_model: SolidModel for lit rendering
            material: material dict (from engine.materials)
        """
        self.position = position if position else Vector3(0, 0, 0)
        self.model = model
        self.solid_model = solid_model
        self.material = material
        self.velocity = Vector3(0, 0, 0)
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = (1.0, 1.0, 1.0)
        self.alive = True
        self.radius = 1.0

    def update(self, dt):
        self.position = self.position + self.velocity * dt

    def get_radius(self):
        return self.radius

    def set_position(self, x, y, z):
        self.position = Vector3(x, y, z)

    def set_velocity(self, x, y, z):
        self.velocity = Vector3(x, y, z)

    def set_rotation(self, rx, ry, rz):
        self.rotation = [rx, ry, rz]

    def rotate(self, drx, dry, drz):
        self.rotation[0] += drx
        self.rotation[1] += dry
        self.rotation[2] += drz

    def set_scale(self, sx, sy, sz):
        self.scale = (sx, sy, sz)

    def destroy(self):
        self.alive = False

    def is_alive(self):
        return self.alive

    def get_color(self):
        return (1.0, 1.0, 1.0)

    def __repr__(self):
        return f"{self.__class__.__name__}(pos={self.position}, alive={self.alive})"
