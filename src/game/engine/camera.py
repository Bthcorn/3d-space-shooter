"""First-person camera system"""

import math
from game.utils.math_utils import Vector3, clamp
from game.config import CAMERA_YAW_LIMIT


class Camera:
    """First-person camera with mouse look"""

    def __init__(self, position=None, yaw=-90.0, pitch=0.0):
        """
        Args:
            position: Camera position (Vector3)
            yaw: Horizontal rotation in degrees
            pitch: Vertical rotation in degrees
        """
        self.position = position if position else Vector3(0, 0, 0)
        self.yaw = yaw  # Left/right
        self.pitch = pitch  # Up/down

        # Camera vectors
        self.front = Vector3(0, 0, -1)
        self.up = Vector3(0, 1, 0)
        self.right = Vector3(1, 0, 0)
        self.world_up = Vector3(0, 1, 0)

        self.update_vectors()

    def update_vectors(self):
        """Update camera direction vectors based on yaw and pitch"""
        # Calculate new front vector
        front_x = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front_y = math.sin(math.radians(self.pitch))
        front_z = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))

        self.front = Vector3(front_x, front_y, front_z).normalize()

        # Recalculate right and up vectors
        self.right = self.front.cross(self.world_up).normalize()
        self.up = self.right.cross(self.front).normalize()

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        """
        Process mouse movement for camera rotation

        Args:
            xoffset: Horizontal mouse offset
            yoffset: Vertical mouse offset
            constrain_pitch: Prevent camera flipping
        """
        self.yaw += xoffset
        self.pitch += yoffset

        # Constrain pitch to prevent screen flip
        if constrain_pitch:
            self.pitch = clamp(self.pitch, -CAMERA_YAW_LIMIT, CAMERA_YAW_LIMIT)

        self.update_vectors()

    def move_forward(self, distance):
        """Move camera forward"""
        self.position = self.position + self.front * distance

    def move_backward(self, distance):
        """Move camera backward"""
        self.position = self.position - self.front * distance

    def move_right(self, distance):
        """Strafe right"""
        self.position = self.position + self.right * distance

    def move_left(self, distance):
        """Strafe left"""
        self.position = self.position - self.right * distance

    def move_up(self, distance):
        """Move up"""
        self.position = self.position + self.up * distance

    def move_down(self, distance):
        """Move down"""
        self.position = self.position - self.up * distance

    def get_view_target(self):
        """Get the point the camera is looking at"""
        return self.position + self.front

    def get_forward_vector(self):
        """Get forward direction (for shooting)"""
        return self.front.copy()

    def __repr__(self):
        return f"Camera(pos={self.position}, yaw={self.yaw:.1f}, pitch={self.pitch:.1f})"
