"""Heads-Up Display (HUD) system — Mini Game 2.

Renders a 2D overlay showing at least 5 live values:
  1. FPS
  2. Player position + heading
  3. Time-of-day factor
  4. Score
  5. Lives / Health
  6. Night-vision / radar status

All rendering is wrapped in push/pop of projection, modelview, and attrib
so that 3D lighting and depth states are not corrupted.
"""

import pygame
import math
from OpenGL.GL import *

from game.config import WINDOW_WIDTH, WINDOW_HEIGHT


class HUD:
    """Heads-up display for game information."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        pygame.font.init()
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 72)

    # ------------------------------------------------------------------
    # Main render
    # ------------------------------------------------------------------

    def render(
        self,
        lives,
        score,
        player_cooldown=0,
        ship_roll=0.0,
        damage_flash=0.0,
        player_pos=None,
        player_yaw=0.0,
        sway_offset=0.0,
        fps=0,
        day_factor=1.0,
        time_label="Day",
        flashlight_on=False,
        night_vision=False,
        radar_active=False,
        enemies=None,
        camera=None,
    ):
        """Render the HUD overlay.

        The method saves and restores ALL relevant GL state so that
        lighting/depth/blending are not corrupted after the call.
        """
        # Save state
        glPushAttrib(GL_ALL_ATTRIB_BITS)

        # Switch to 2D ortho
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # --- cockpit rotating elements ---
        glPushMatrix()
        cx, cy = self.width // 2, self.height // 2

        glTranslatef(sway_offset, 0, 0)
        glTranslatef(cx, cy, 0)
        glRotatef(ship_roll, 0, 0, 1)
        glTranslatef(-cx, -cy, 0)

        hud_color = (0.2, 0.8, 1.0, 0.8)
        warning_color = (1.0, 0.2, 0.2, 0.8)

        # Damage flash tint
        if damage_flash > 0:
            glColor4f(*warning_color)
        else:
            glColor4f(*hud_color)

        radius = min(self.width, self.height) * 0.4

        # Left arc
        self._draw_arc(cx, cy, radius, 140, 220, 3.0)
        self._draw_ticks_on_arc(cx, cy, radius + 10, 140, 220, 5, 10)

        # Right arc (cooldown colour)
        if player_cooldown > 0:
            glColor4f(*warning_color)
        else:
            glColor4f(*hud_color)
        self._draw_arc(cx, cy, radius, -40, 40, 3.0)
        self._draw_ticks_on_arc(cx, cy, radius + 10, -40, 40, 5, 10)

        glColor4f(*hud_color)

        # Dashboard nose
        dashboard_y = cy - radius * 0.65
        self._draw_dashboard(cx, dashboard_y, radius)

        # Cockpit struts
        self._draw_cockpit_struts(cx, cy, self.width, self.height)

        glPopMatrix()  # end cockpit rotation block

        # --- Centre reticle (fixed, no sway) ---
        glColor4f(*hud_color)
        self._draw_reticle(cx, cy)

        # --- Static text elements ---
        # Lives
        self._draw_life_blocks(50, self.height - 50, lives)

        # Score
        self._render_text(f"SCORE: {score}", self.width - 200, self.height - 50, self.font)

        # FPS (always shown)
        self._render_text(f"FPS: {fps}", self.width - 100, 20, self.small_font)

        # Player position & heading
        if player_pos is not None:
            pos_text = f"POS: ({player_pos.x:.0f}, {player_pos.y:.0f}, {player_pos.z:.0f})"
            self._render_text(pos_text, 20, 65, self.small_font)
        heading_text = f"HDG: {player_yaw:.0f}°"
        self._render_text(heading_text, 20, 45, self.small_font)

        # Time of day
        day_pct = int(day_factor * 100)
        self._render_text(f"TIME: {time_label} ({day_pct}%)", 20, 25, self.small_font)

        # Night-vision / radar indicators
        indicators = []
        if night_vision:
            indicators.append("[NV]")
        if radar_active:
            indicators.append("[RADAR]")
        if indicators:
            self._render_text("  ".join(indicators),
                              self.width // 2 - 80, 25, self.small_font)

        # --- Radar / Detection overlay ---
        if radar_active and enemies is not None and camera is not None:
            self._draw_radar(enemies, camera, player_pos)
            self._draw_enemy_screen_brackets(enemies, camera)

        # --- Restore state ---
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glPopAttrib()  # restores depth, lighting, blend, etc.

    # ------------------------------------------------------------------
    # Radar / Detection system
    # ------------------------------------------------------------------

    def _draw_radar(self, enemies, camera, player_pos):
        """Draw a circular radar mini-map in the top-right corner.

        Player is at center, forward direction is up.
        Enemy dots are plotted relative to player position and heading.
        """
        radar_radius = 70
        radar_cx = self.width - radar_radius - 30
        radar_cy = self.height - radar_radius - 80
        radar_range = 120.0  # World units the radar covers

        # Background circle (dark, semi-transparent)
        glColor4f(0.0, 0.05, 0.1, 0.6)
        self._draw_filled_circle(radar_cx, radar_cy, radar_radius)

        # Outer ring
        glColor4f(0.1, 0.8, 0.4, 0.7)
        glLineWidth(2.0)
        self._draw_circle_outline(radar_cx, radar_cy, radar_radius)

        # Inner range ring (half range)
        glColor4f(0.1, 0.6, 0.3, 0.35)
        glLineWidth(1.0)
        self._draw_circle_outline(radar_cx, radar_cy, radar_radius * 0.5)

        # Crosshair lines
        glColor4f(0.1, 0.6, 0.3, 0.3)
        glBegin(GL_LINES)
        glVertex2f(radar_cx, radar_cy - radar_radius)
        glVertex2f(radar_cx, radar_cy + radar_radius)
        glVertex2f(radar_cx - radar_radius, radar_cy)
        glVertex2f(radar_cx + radar_radius, radar_cy)
        glEnd()

        # Player dot (center, bright green)
        glColor4f(0.2, 1.0, 0.4, 1.0)
        glPointSize(5.0)
        glBegin(GL_POINTS)
        glVertex2f(radar_cx, radar_cy)
        glEnd()

        # Player forward indicator (small triangle pointing up)
        glBegin(GL_TRIANGLES)
        glVertex2f(radar_cx, radar_cy + 8)
        glVertex2f(radar_cx - 3, radar_cy + 3)
        glVertex2f(radar_cx + 3, radar_cy + 3)
        glEnd()

        # Plot enemies
        if player_pos is None:
            return

        # Rotation angle: maps camera forward to "up" on radar
        yaw_rad = math.radians(camera.yaw)
        rot_angle = math.pi / 2.0 - yaw_rad
        cos_a = math.cos(rot_angle)
        sin_a = math.sin(rot_angle)

        for enemy in enemies:
            # Offset from player in world space
            dx = enemy.position.x - player_pos.x
            dz = enemy.position.z - player_pos.z
            dist = math.sqrt(dx * dx + dz * dz)

            if dist > radar_range:
                # Clamp to edge of radar
                scale = radar_range / dist
                dx *= scale
                dz *= scale
                dist = radar_range

            # Rotate world offset into radar-local coordinates
            # ry = forward (up on radar), rx = right (right on radar)
            rx = -(dx * cos_a - dz * sin_a)
            ry = dx * sin_a + dz * cos_a

            # Map to radar pixel coords
            px = radar_cx + (rx / radar_range) * radar_radius
            py = radar_cy + (ry / radar_range) * radar_radius

            # Colour: bright red if close, dimmer if far
            intensity = max(0.3, 1.0 - dist / radar_range)
            glColor4f(1.0, 0.2, 0.1, intensity)

            # Dot size based on distance
            dot_size = max(3.0, 6.0 - (dist / radar_range) * 3.0)
            glPointSize(dot_size)
            glBegin(GL_POINTS)
            glVertex2f(px, py)
            glEnd()

        glPointSize(1.0)

        # Label
        glColor4f(0.1, 0.8, 0.4, 0.8)
        self._render_text("RADAR", radar_cx - 18,
                          radar_cy + radar_radius + 8, self.small_font)
        enemy_count = len(enemies)
        self._render_text(f"TGT: {enemy_count}", radar_cx - 18,
                          radar_cy - radar_radius - 18, self.small_font)

    def _draw_enemy_screen_brackets(self, enemies, camera):
        """Draw red square brackets on enemies visible on screen.

        Projects each enemy's 3D position to 2D screen coordinates.
        If within the viewport, draws red corner brackets + distance label.
        """
        from game.config import FOV, NEAR_PLANE, FAR_PLANE

        # Read back current OpenGL matrices for projection
        proj = glGetDoublev(GL_PROJECTION_MATRIX)
        modl = glGetDoublev(GL_MODELVIEW_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        from OpenGL.GLU import gluProject

        for enemy in enemies:
            try:
                sx, sy, sz = gluProject(
                    enemy.position.x, enemy.position.y, enemy.position.z,
                    modl, proj, viewport,
                )
            except Exception:
                continue

            # sz < 0 or > 1 means behind camera or beyond far plane
            if sz < 0.0 or sz > 1.0:
                continue

            # Check if within screen bounds (with margin)
            margin = 40
            if sx < -margin or sx > self.width + margin:
                continue
            if sy < -margin or sy > self.height + margin:
                continue

            # Distance from player
            dx = enemy.position.x - camera.position.x
            dy = enemy.position.y - camera.position.y
            dz = enemy.position.z - camera.position.z
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)

            # Square bracket half-size scales with proximity
            half = max(14, min(35, 500.0 / max(dist, 1.0)))
            corner_len = half * 0.4  # length of each L-corner stroke

            # Always red
            glColor4f(1.0, 0.15, 0.1, 0.9)
            glLineWidth(2.0)

            # Four L-shaped corners forming a square bracket
            glBegin(GL_LINES)

            # Top-left corner
            glVertex2f(sx - half, sy + half)
            glVertex2f(sx - half + corner_len, sy + half)
            glVertex2f(sx - half, sy + half)
            glVertex2f(sx - half, sy + half - corner_len)

            # Top-right corner
            glVertex2f(sx + half, sy + half)
            glVertex2f(sx + half - corner_len, sy + half)
            glVertex2f(sx + half, sy + half)
            glVertex2f(sx + half, sy + half - corner_len)

            # Bottom-left corner
            glVertex2f(sx - half, sy - half)
            glVertex2f(sx - half + corner_len, sy - half)
            glVertex2f(sx - half, sy - half)
            glVertex2f(sx - half, sy - half + corner_len)

            # Bottom-right corner
            glVertex2f(sx + half, sy - half)
            glVertex2f(sx + half - corner_len, sy - half)
            glVertex2f(sx + half, sy - half)
            glVertex2f(sx + half, sy - half + corner_len)

            glEnd()

            # Distance label below bracket
            dist_text = f"{dist:.0f}m"
            self._render_text(dist_text, int(sx) - 12,
                              int(sy) - int(half) - 16, self.small_font)

        glLineWidth(1.0)

    # ------------------------------------------------------------------
    # Radar shape helpers
    # ------------------------------------------------------------------

    def _draw_filled_circle(self, cx, cy, radius, segments=36):
        """Draw a filled circle."""
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for i in range(segments + 1):
            theta = 2.0 * math.pi * i / segments
            glVertex2f(cx + math.cos(theta) * radius,
                       cy + math.sin(theta) * radius)
        glEnd()

    def _draw_circle_outline(self, cx, cy, radius, segments=48):
        """Draw a circle outline."""
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            glVertex2f(cx + math.cos(theta) * radius,
                       cy + math.sin(theta) * radius)
        glEnd()

    # ------------------------------------------------------------------
    # Game over / pause overlays
    # ------------------------------------------------------------------

    def render_game_over(self, final_score):
        """Render game-over screen."""
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # Dark overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height); glVertex2f(0, self.height)
        glEnd()

        self._render_text("GAME OVER",
                          self.width // 2 - 150, self.height // 2 + 50, self.large_font)
        self._render_text(f"Final Score: {final_score}",
                          self.width // 2 - 80, self.height // 2 - 20, self.font)
        self._render_text("Press R to Restart or ESC to Quit",
                          self.width // 2 - 120, self.height // 2 - 80, self.small_font)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()

    def render_pause(self):
        """Render pause screen."""
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height); glVertex2f(0, self.height)
        glEnd()

        self._render_text("PAUSED",
                          self.width // 2 - 100, self.height // 2 + 20, self.large_font)
        self._render_text("Press ESC to Resume",
                          self.width // 2 - 90, self.height // 2 - 40, self.small_font)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------

    def resize(self, width, height):
        self.width = width
        self.height = height

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _render_text(self, text, x, y, font):
        """Render text at (x, y) bottom-left origin using glDrawPixels."""
        text_surface = font.render(text, True, (200, 240, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        tw, th = text_surface.get_size()

        glRasterPos2f(x, y)
        glDrawPixels(tw, th, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def _draw_reticle(self, cx, cy):
        gap, length = 10, 20
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(cx, cy + gap); glVertex2f(cx, cy + gap + length)
        glVertex2f(cx + _cos(210) * gap, cy + _sin(210) * gap)
        glVertex2f(cx + _cos(210) * (gap + length), cy + _sin(210) * (gap + length))
        glVertex2f(cx + _cos(330) * gap, cy + _sin(330) * gap)
        glVertex2f(cx + _cos(330) * (gap + length), cy + _sin(330) * (gap + length))
        glEnd()
        glPointSize(2.0)
        glBegin(GL_POINTS); glVertex2f(cx, cy); glEnd()
        glPointSize(1.0)
        glLineWidth(1.0)

    def _draw_cockpit_struts(self, cx, cy, w, h):
        glLineWidth(3.0)
        glColor4f(0.4, 0.4, 0.5, 0.8)
        glBegin(GL_LINE_LOOP)
        glVertex2f(0, 0); glVertex2f(w * 0.2, h * 0.4)
        glVertex2f(w * 0.1, h * 0.9); glVertex2f(0, h)
        glEnd()
        glBegin(GL_LINE_LOOP)
        glVertex2f(w, 0); glVertex2f(w * 0.8, h * 0.4)
        glVertex2f(w * 0.9, h * 0.9); glVertex2f(w, h)
        glEnd()
        glColor4f(0.2, 0.8, 1.0, 0.8)
        glLineWidth(1.0)

    def _draw_dashboard(self, cx, top_y, radius):
        glLineWidth(2.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(cx - radius * 0.6, 0)
        glVertex2f(cx - radius * 0.4, top_y)
        glVertex2f(cx + radius * 0.4, top_y)
        glVertex2f(cx + radius * 0.6, 0)
        glEnd()
        glBegin(GL_LINES)
        glVertex2f(cx, 0); glVertex2f(cx, top_y)
        glEnd()
        glLineWidth(1.0)

    def _draw_life_blocks(self, x, y, lives):
        bw, bh, sp = 25, 10, 5
        if lives <= 1:
            glColor4f(1.0, 0.2, 0.2, 0.8)
        else:
            glColor4f(0.2, 0.8, 1.0, 0.8)
        glBegin(GL_QUADS)
        for i in range(lives):
            bx = x + i * (bw + sp)
            glVertex2f(bx, y); glVertex2f(bx + bw, y)
            glVertex2f(bx + bw, y + bh); glVertex2f(bx, y + bh)
        glEnd()

    def _draw_arc(self, cx, cy, radius, start_deg, end_deg, thickness):
        glLineWidth(thickness)
        glBegin(GL_LINE_STRIP)
        segs = 50
        s, e = math.radians(start_deg), math.radians(end_deg)
        for i in range(segs + 1):
            t = s + (e - s) * i / segs
            glVertex2f(cx + math.cos(t) * radius, cy + math.sin(t) * radius)
        glEnd()
        glLineWidth(1.0)

    def _draw_ticks_on_arc(self, cx, cy, radius, start_deg, end_deg, n, length):
        glLineWidth(2.0)
        glBegin(GL_LINES)
        s, e = math.radians(start_deg), math.radians(end_deg)
        for i in range(n):
            t = s + (e - s) * i / (n - 1)
            c, si = math.cos(t), math.sin(t)
            glVertex2f(cx + c * radius, cy + si * radius)
            glVertex2f(cx + c * (radius + length), cy + si * (radius + length))
        glEnd()
        glLineWidth(1.0)


# ------------------------------------------------------------------
# Tiny helpers
# ------------------------------------------------------------------

def _cos(deg):
    return math.cos(math.radians(deg))

def _sin(deg):
    return math.sin(math.radians(deg))
