"""Math utilities — Vector3, matrix operations, helpers."""

import math
import numpy as np


class Vector3:
    """Simple 3D vector."""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self):
        l = self.length()
        if l > 1e-8:
            return Vector3(self.x / l, self.y / l, self.z / l)
        return Vector3(0, 0, 0)

    def distance_to(self, other):
        return (self - other).length()

    def copy(self):
        return Vector3(self.x, self.y, self.z)

    def __repr__(self):
        return f"V3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


# ---- Matrix helpers (4x4) ----

def translation_matrix(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx], [0, 1, 0, ty],
        [0, 0, 1, tz], [0, 0, 0, 1],
    ], dtype=np.float32)


def rotation_matrix_x(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [1, 0, 0, 0], [0, c, -s, 0],
        [0, s, c, 0], [0, 0, 0, 1],
    ], dtype=np.float32)


def rotation_matrix_y(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [c, 0, s, 0], [0, 1, 0, 0],
        [-s, 0, c, 0], [0, 0, 0, 1],
    ], dtype=np.float32)


def rotation_matrix_z(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [c, -s, 0, 0], [s, c, 0, 0],
        [0, 0, 1, 0], [0, 0, 0, 1],
    ], dtype=np.float32)


def scale_matrix(sx, sy, sz):
    return np.array([
        [sx, 0, 0, 0], [0, sy, 0, 0],
        [0, 0, sz, 0], [0, 0, 0, 1],
    ], dtype=np.float32)


def perspective_matrix(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0],
    ], dtype=np.float32)


def look_at_matrix(eye, target, up):
    z_axis = (eye - target).normalize()
    x_axis = up.cross(z_axis).normalize()
    y_axis = z_axis.cross(x_axis)
    return np.array([
        [x_axis.x, x_axis.y, x_axis.z, -x_axis.dot(eye)],
        [y_axis.x, y_axis.y, y_axis.z, -y_axis.dot(eye)],
        [z_axis.x, z_axis.y, z_axis.z, -z_axis.dot(eye)],
        [0, 0, 0, 1],
    ], dtype=np.float32)


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def lerp(a, b, t):
    return a + (b - a) * t
