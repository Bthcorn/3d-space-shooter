"""Mathematical utilities for 3D transformations"""

import numpy as np
import math


class Vector3:
    """3D Vector class"""

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

    def __truediv__(self, scalar):
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        """Dot product"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """Cross product"""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self):
        """Vector magnitude"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        """Return normalized vector"""
        length = self.length()
        if length > 0:
            return self / length
        return Vector3(0, 0, 0)

    def distance_to(self, other):
        """Distance to another vector"""
        return (self - other).length()

    def to_tuple(self):
        """Convert to tuple"""
        return (self.x, self.y, self.z)

    def copy(self):
        """Return a copy of this vector"""
        return Vector3(self.x, self.y, self.z)

    def __repr__(self):
        return f"Vector3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


def rotation_matrix_x(angle):
    """Create rotation matrix around X axis"""
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=np.float32)


def rotation_matrix_y(angle):
    """Create rotation matrix around Y axis"""
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], dtype=np.float32)


def rotation_matrix_z(angle):
    """Create rotation matrix around Z axis"""
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32)


def translation_matrix(x, y, z):
    """Create translation matrix"""
    return np.array([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]], dtype=np.float32)


def scale_matrix(sx, sy, sz):
    """Create scale matrix"""
    return np.array([[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]], dtype=np.float32)


def perspective_matrix(fov, aspect, near, far):
    """Create perspective projection matrix"""
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    return np.array(
        [
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
            [0, 0, -1, 0],
        ],
        dtype=np.float32,
    )


def look_at_matrix(eye, target, up):
    """Create view matrix using look-at"""
    z_axis = (eye - target).normalize()
    x_axis = up.cross(z_axis).normalize()
    y_axis = z_axis.cross(x_axis)

    return np.array(
        [
            [x_axis.x, x_axis.y, x_axis.z, -x_axis.dot(eye)],
            [y_axis.x, y_axis.y, y_axis.z, -y_axis.dot(eye)],
            [z_axis.x, z_axis.y, z_axis.z, -z_axis.dot(eye)],
            [0, 0, 0, 1],
        ],
        dtype=np.float32,
    )


def clamp(value, min_value, max_value):
    """Clamp value between min and max"""
    return max(min_value, min(max_value, value))


def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t
