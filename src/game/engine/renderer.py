"""OpenGL wireframe renderer"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from game.config import (
    FOV,
    NEAR_PLANE,
    FAR_PLANE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)
from game.utils.math_utils import (
    perspective_matrix,
    look_at_matrix,
    translation_matrix,
    rotation_matrix_x,
    rotation_matrix_y,
    rotation_matrix_z,
    clamp,
)


class Renderer:
    """OpenGL wireframe renderer"""

    def __init__(self, width, height):
        """
        Initialize OpenGL renderer

        Args:
            width, height: Window dimensions
        """
        self.width = width
        self.height = height
        self.aspect_ratio = width / height

        # Initialize OpenGL
        self._init_opengl()

    def _init_opengl(self):
        """Initialize OpenGL settings"""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Set line width for wireframe
        glLineWidth(1.5)

        # Set clear color (Deep Space Blue/Purple)
        glClearColor(0.05, 0.05, 0.1, 1.0)

        # Set up projection matrix
        self.projection_matrix = perspective_matrix(FOV, self.aspect_ratio, NEAR_PLANE, FAR_PLANE)

    def begin_frame(self):
        """Start rendering a new frame"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def end_frame(self):
        """Finish rendering frame"""
        pygame.display.flip()

    def set_view_matrix(self, camera):
        """
        Set view matrix from camera

        Args:
            camera: Camera object
        """
        self.view_matrix = look_at_matrix(camera.position, camera.get_view_target(), camera.up)

    def render_wireframe(
        self, model, position, rotation=(0, 0, 0), scale=(1, 1, 1), color=(1, 1, 1)
    ):
        """
        Render a wireframe model

        Args:
            model: WireframeModel object
            position: Position vector (Vector3)
            rotation: Rotation angles in radians (rx, ry, rz)
            scale: Scale factors (sx, sy, sz)
            color: RGB color tuple
        """
        glPushMatrix()

        # Apply transformations
        # 1. Translation
        glTranslatef(position.x, position.y, position.z)

        # 2. Rotation
        if rotation[0] != 0:
            glRotatef(np.degrees(rotation[0]), 1, 0, 0)
        if rotation[1] != 0:
            glRotatef(np.degrees(rotation[1]), 0, 1, 0)
        if rotation[2] != 0:
            glRotatef(np.degrees(rotation[2]), 0, 0, 1)

        # 3. Scale
        glScalef(scale[0], scale[1], scale[2])

        # Set color
        glColor3f(*color)

        # Draw wireframe
        glBegin(GL_LINES)
        for edge in model.edges:
            for vertex_idx in edge:
                vertex = model.vertices[vertex_idx]
                glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

        glPopMatrix()

    def apply_camera(self, camera):
        """Apply camera transformations"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, self.aspect_ratio, NEAR_PLANE, FAR_PLANE)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Look from camera position to target
        target = camera.get_view_target()
        gluLookAt(
            camera.position.x,
            camera.position.y,
            camera.position.z,
            target.x,
            target.y,
            target.z,
            camera.up.x,
            camera.up.y,
            camera.up.z,
        )

    def render_line(self, start, end, color=(1, 1, 1)):
        """
        Render a single line (for debugging or effects)

        Args:
            start, end: Vector3 positions
            color: RGB color tuple
        """
        glColor3f(*color)
        glBegin(GL_LINES)
        glVertex3f(start.x, start.y, start.z)
        glVertex3f(end.x, end.y, end.z)
        glEnd()

    def render_crosshair(self):
        """Render crosshair in screen center"""
        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Disable depth test for 2D overlay
        glDisable(GL_DEPTH_TEST)

        # Draw crosshair
        size = 10
        center_x = self.width / 2
        center_y = self.height / 2

        glColor3f(0, 1, 0)  # Green crosshair
        glLineWidth(2.0)

        glBegin(GL_LINES)
        # Horizontal line
        glVertex2f(center_x - size, center_y)
        glVertex2f(center_x + size, center_y)
        # Vertical line
        glVertex2f(center_x, center_y - size)
        glVertex2f(center_x, center_y + size)
        glEnd()

        glLineWidth(1.5)  # Reset line width

        # Re-enable depth test
        glEnable(GL_DEPTH_TEST)

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def render_player_ship(self, player, camera, ship_roll=0.0, ship_pitch_offset=0.0):
        """
        Render player ship LOCKED to camera view (true cockpit mode)
        Ship stays at exact same screen position regardless of camera movement

        Args:
            player: Player entity
            camera: Camera object
            ship_roll: Banking angle (degrees) when turning
            ship_pitch_offset: Additional pitch angle (degrees) from camera movement
        """
        from game.config import (
            PLAYER_SHIP_OFFSET_FORWARD,
            PLAYER_SHIP_OFFSET_DOWN,
            PLAYER_SHIP_OFFSET_RIGHT,
            PLAYER_SHIP_SCALE,
        )

        # Clamp input values for safety
        ship_roll = clamp(ship_roll, -45, 45)
        ship_pitch_offset = clamp(ship_pitch_offset, -30, 30)

        glPushMatrix()

        # Calculate ship world position VERY EXPLICITLY
        # This ensures ship is always locked to camera

        # Start with camera world position
        ship_x = camera.position.x
        ship_y = camera.position.y
        ship_z = camera.position.z

        # Add forward offset (negative = in front of camera)
        ship_x += camera.front.x * PLAYER_SHIP_OFFSET_FORWARD
        ship_y += camera.front.y * PLAYER_SHIP_OFFSET_FORWARD
        ship_z += camera.front.z * PLAYER_SHIP_OFFSET_FORWARD

        # Add up/down offset (negative = down)
        ship_x += camera.up.x * PLAYER_SHIP_OFFSET_DOWN
        ship_y += camera.up.y * PLAYER_SHIP_OFFSET_DOWN
        ship_z += camera.up.z * PLAYER_SHIP_OFFSET_DOWN

        # Add left/right offset
        ship_x += camera.right.x * PLAYER_SHIP_OFFSET_RIGHT
        ship_y += camera.right.y * PLAYER_SHIP_OFFSET_RIGHT
        ship_z += camera.right.z * PLAYER_SHIP_OFFSET_RIGHT

        # Position ship at calculated world position
        glTranslatef(ship_x, ship_y, ship_z)

        # Match camera orientation EXACTLY
        # Yaw (horizontal rotation)
        glRotatef(-camera.yaw - 90, 0, 1, 0)

        # Pitch (vertical rotation) with animation offset
        total_pitch = camera.pitch + ship_pitch_offset
        glRotatef(total_pitch, 1, 0, 0)

        # Roll (banking effect)
        glRotatef(ship_roll, 0, 0, 1)

        # Scale ship
        scale_factor = PLAYER_SHIP_SCALE
        glScalef(scale_factor, scale_factor, scale_factor)

        # Set color
        glColor3f(*player.get_color())

        # Draw wireframe
        glBegin(GL_LINES)
        for edge in player.model.edges:
            for vertex_idx in edge:
                vertex = player.model.vertices[vertex_idx]
                glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

        glPopMatrix()

    def resize(self, width, height):
        """Handle window resize"""
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        glViewport(0, 0, width, height)
        self.projection_matrix = perspective_matrix(FOV, self.aspect_ratio, NEAR_PLANE, FAR_PLANE)
