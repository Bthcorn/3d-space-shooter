"""OpenGL renderer — solid + wireframe, material-aware, transparency-correct.

Replaces the original pure-wireframe renderer with full fixed-pipeline
lighting and material support for Mini Game 2.
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random as _random

from game.config import (
    FOV, NEAR_PLANE, FAR_PLANE,
    PLAYER_SHIP_OFFSET_FORWARD, PLAYER_SHIP_OFFSET_DOWN,
    PLAYER_SHIP_OFFSET_RIGHT, PLAYER_SHIP_SCALE,
    STAR_COUNT,
)
from game.engine.materials import apply_material
from game.utils.math_utils import (
    perspective_matrix, look_at_matrix,
    clamp,
)


class Renderer:
    """OpenGL renderer with solid geometry, lighting, and transparency."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        self._init_opengl()

        # Transparency queue: collect transparent draw-calls, render last
        self._transparent_queue = []

        # Pre-generate star positions on a unit sphere (scaled at render time)
        self._star_verts = []
        rng = _random.Random(42)  # fixed seed → same stars every run
        for _ in range(STAR_COUNT):
            # Uniform sphere sampling (rejection method)
            while True:
                x = rng.uniform(-1, 1)
                y = rng.uniform(-1, 1)
                z = rng.uniform(-1, 1)
                d = math.sqrt(x * x + y * y + z * z)
                if 0.001 < d <= 1.0:
                    inv = 1.0 / d
                    self._star_verts.append((x * inv, y * inv, z * inv))
                    break
        # Per-star brightness (0.4 – 1.0) and size (1 – 3)
        self._star_brightness = [rng.uniform(0.4, 1.0) for _ in self._star_verts]
        self._star_size       = [rng.choice([1.0, 1.0, 1.0, 2.0, 3.0])
                                  for _ in self._star_verts]

    # ------------------------------------------------------------------
    # OpenGL init
    # ------------------------------------------------------------------

    def _init_opengl(self):
        """One-time OpenGL state setup."""
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Will be overridden each frame by the lighting system
        glClearColor(0.05, 0.05, 0.1, 1.0)

        # Default line width for any remaining wireframe usage
        glLineWidth(1.5)

        # Back-face culling (optional — helps perf, ensures correct normals)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)

        # Projection
        self.projection_matrix = perspective_matrix(FOV, self.aspect_ratio, NEAR_PLANE, FAR_PLANE)

    # ------------------------------------------------------------------
    # Frame begin / end
    # ------------------------------------------------------------------

    def begin_frame(self):
        """Clear buffers at start of frame."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._transparent_queue.clear()

    def end_frame(self):
        """Swap buffers."""
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------

    def apply_camera(self, camera):
        """Set projection + modelview from camera."""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV, self.aspect_ratio, NEAR_PLANE, FAR_PLANE)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        t = camera.get_view_target()
        gluLookAt(
            camera.position.x, camera.position.y, camera.position.z,
            t.x, t.y, t.z,
            camera.up.x, camera.up.y, camera.up.z,
        )

    # ------------------------------------------------------------------
    # Solid rendering
    # ------------------------------------------------------------------

    def render_solid(self, model, position, rotation=(0, 0, 0),
                     scale=(1, 1, 1), material=None):
        """Render a SolidModel with the given material.

        If the material has alpha < 1, the draw call is deferred to the
        transparency pass.

        Args:
            model: SolidModel object
            position: Vector3
            rotation: (rx, ry, rz) in radians
            scale: (sx, sy, sz)
            material: material dict (from materials.py)
        """
        if material and material.get("alpha", 1.0) < 1.0:
            # Queue for later transparent pass
            self._transparent_queue.append(
                (model, position, rotation, scale, material)
            )
            return

        self._draw_solid(model, position, rotation, scale, material)

    def _draw_solid(self, model, position, rotation, scale, material):
        """Internal: immediately draw a solid model."""
        glPushMatrix()

        # Transform
        glTranslatef(position.x, position.y, position.z)
        if rotation[0] != 0:
            glRotatef(np.degrees(rotation[0]), 1, 0, 0)
        if rotation[1] != 0:
            glRotatef(np.degrees(rotation[1]), 0, 1, 0)
        if rotation[2] != 0:
            glRotatef(np.degrees(rotation[2]), 0, 0, 1)
        glScalef(scale[0], scale[1], scale[2])

        # Apply material
        if material:
            apply_material(material)

        # Draw faces
        for i, face in enumerate(model.faces):
            normal = model.normals[i]
            glNormal3f(*normal)

            if len(face) == 3:
                glBegin(GL_TRIANGLES)
            elif len(face) == 4:
                glBegin(GL_QUADS)
            else:
                glBegin(GL_POLYGON)

            for vi in face:
                v = model.vertices[vi]
                glVertex3f(v[0], v[1], v[2])
            glEnd()

        glPopMatrix()

    # ------------------------------------------------------------------
    # Transparent pass
    # ------------------------------------------------------------------

    def render_transparent_objects(self, camera_pos=None):
        """Draw all queued transparent objects back-to-front.

        Call AFTER all opaque objects have been rendered.
        """
        if not self._transparent_queue:
            return

        # Sort back-to-front by distance to camera (furthest first)
        if camera_pos is not None:
            self._transparent_queue.sort(
                key=lambda item: -(
                    (item[1].x - camera_pos.x) ** 2 +
                    (item[1].y - camera_pos.y) ** 2 +
                    (item[1].z - camera_pos.z) ** 2
                )
            )

        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # Disable depth WRITING (but keep depth TEST)
        glDepthMask(GL_FALSE)
        # Disable back-face culling for transparent objects (see both sides)
        glDisable(GL_CULL_FACE)

        for model, position, rotation, scale, material in self._transparent_queue:
            self._draw_solid(model, position, rotation, scale, material)

        # Restore state
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glEnable(GL_CULL_FACE)

        self._transparent_queue.clear()

    # ------------------------------------------------------------------
    # Starfield background
    # ------------------------------------------------------------------

    def render_starfield(self, camera_pos, day_factor=1.0):
        """Draw stars as GL_POINTS on a large sphere centred on the camera.

        Rendered before any opaque geometry with depth-write OFF so stars
        always sit in the background without z-fighting.
        """
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Stars dim a little when the "sun" is brightest but never vanish
        dim = 0.55 + 0.45 * (1.0 - day_factor)
        radius = FAR_PLANE * 0.85  # just inside the far plane

        cx, cy, cz = camera_pos.x, camera_pos.y, camera_pos.z

        # Group by point size to minimise glPointSize calls
        from itertools import groupby
        sorted_stars = sorted(
            zip(self._star_size, self._star_brightness, self._star_verts),
            key=lambda t: t[0],
        )
        for sz, group in groupby(sorted_stars, key=lambda t: t[0]):
            glPointSize(sz)
            glBegin(GL_POINTS)
            for _, brightness, (sx, sy, sz_) in group:
                b = brightness * dim
                glColor4f(b * 0.85 + 0.15, b * 0.88 + 0.12, b, b)
                glVertex3f(cx + sx * radius, cy + sy * radius, cz + sz_ * radius)
            glEnd()

        glPointSize(1.0)
        glDepthMask(GL_TRUE)
        glPopAttrib()

    # ------------------------------------------------------------------
    # Legacy wireframe rendering (optional, kept for debug)
    # ------------------------------------------------------------------

    def render_wireframe(self, model, position, rotation=(0, 0, 0),
                         scale=(1, 1, 1), color=(1, 1, 1)):
        """Render a WireframeModel (no lighting)."""
        glPushMatrix()
        glDisable(GL_LIGHTING)

        glTranslatef(position.x, position.y, position.z)
        if rotation[0] != 0:
            glRotatef(np.degrees(rotation[0]), 1, 0, 0)
        if rotation[1] != 0:
            glRotatef(np.degrees(rotation[1]), 0, 1, 0)
        if rotation[2] != 0:
            glRotatef(np.degrees(rotation[2]), 0, 0, 1)
        glScalef(scale[0], scale[1], scale[2])

        glColor3f(*color)
        glBegin(GL_LINES)
        for edge in model.edges:
            for vi in edge:
                v = model.vertices[vi]
                glVertex3f(v[0], v[1], v[2])
        glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()

    # ------------------------------------------------------------------
    # Ground plane (gives spatial reference)
    # ------------------------------------------------------------------

    def render_ground_plane(self, material, camera_pos, size=200, spacing=10):
        """Render a large grid ground plane at y = -10."""
        glPushMatrix()
        apply_material(material)

        y = -10.0
        half = size / 2
        # Centre grid around camera X, Z
        cx = int(camera_pos.x / spacing) * spacing
        cz = int(camera_pos.z / spacing) * spacing

        glNormal3f(0, 1, 0)
        glBegin(GL_QUADS)
        for ix in range(int(-half), int(half), spacing):
            for iz in range(int(-half), int(half), spacing):
                x = cx + ix
                z = cz + iz
                glVertex3f(x, y, z)
                glVertex3f(x + spacing, y, z)
                glVertex3f(x + spacing, y, z + spacing)
                glVertex3f(x, y, z + spacing)
        glEnd()

        glPopMatrix()

    # ------------------------------------------------------------------
    # Crosshair (2D overlay — no lighting)
    # ------------------------------------------------------------------

    def render_crosshair(self):
        """Draw a simple crosshair in screen centre."""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        size = 10
        cx, cy = self.width / 2, self.height / 2
        glColor3f(0, 1, 0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(cx - size, cy); glVertex2f(cx + size, cy)
        glVertex2f(cx, cy - size); glVertex2f(cx, cy + size)
        glEnd()
        glLineWidth(1.5)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------

    def resize(self, width, height):
        """Handle window resize."""
        if height == 0:
            height = 1
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        glViewport(0, 0, width, height)
        self.projection_matrix = perspective_matrix(FOV, self.aspect_ratio, NEAR_PLANE, FAR_PLANE)
