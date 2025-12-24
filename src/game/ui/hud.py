"""Heads-Up Display (HUD) system"""

import pygame
import math
from OpenGL.GL import *
from game.config import COLOR_HUD, WINDOW_WIDTH, WINDOW_HEIGHT


class HUD:
    """Heads-up display for game information"""

    def __init__(self, width, height):
        """
        Initialize HUD

        Args:
            width, height: Screen dimensions
        """
        self.width = width
        self.height = height
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def render(
        self,
        lives,
        score,
        player_cooldown=0,
        ship_roll=0.0,
        damage_flash=0.0,
        enemies=None,
        player_pos=None,
        player_yaw=0.0,
        sway_offset=0.0,
        fps=0,
    ):
        """
        Render HUD information

        Args:
            lives: Current player lives
            score: Current score
            player_cooldown: Player shoot cooldown (0.0 to 1.0)
            ship_roll: Current ship banking angle in degrees
            damage_flash: Intensity of damage flash (0.0 to 1.0)
            enemies: List of enemy entities
            player_pos: Player position Vector3
            player_yaw: Player yaw in degrees
            fps: Frames per second (optional)
        """
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

        # Enable blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # --- Render ROTATING Cockpit Elements ---
        glPushMatrix()

        cx, cy = self.width // 2, self.height // 2

        # Apply Sway (Translate Horizontal)
        glTranslatef(sway_offset, 0, 0)

        # Apply rotation around screen center
        glTranslatef(cx, cy, 0)
        glRotatef(ship_roll, 0, 0, 1)  # Roll rotates around Z axis
        glTranslatef(-cx, -cy, 0)

        # Color for HUD lines (Light Blue/Cyan)
        hud_color = (0.2, 0.8, 1.0, 0.8)
        warning_color = (1.0, 0.2, 0.2, 0.8)

        # 1. Left Bracket (Speed/Status)
        # Check for damage flash
        if damage_flash > 0:
            glColor4f(*warning_color)
        else:
            glColor4f(*hud_color)

        radius = min(self.width, self.height) * 0.4

        self._draw_arc(cx, cy, radius, 140, 220, 3.0)
        self._draw_ticks_on_arc(cx, cy, radius + 10, 140, 220, 5, 10)

        # 2. Right Bracket (Weapon/Cooldown)
        if player_cooldown > 0:
            glColor4f(*warning_color)
        else:
            glColor4f(*hud_color)

        self._draw_arc(cx, cy, radius, -40, 40, 3.0)
        self._draw_ticks_on_arc(cx, cy, radius + 10, -40, 40, 5, 10)

        # Reset Color
        glColor4f(*hud_color)

        # 4. Wireframe Dashboard/Nose and Radar
        # Lowered position (cy - radius * 0.65)
        dashboard_y = cy - radius * 0.65
        self._draw_dashboard(cx, dashboard_y, radius)
        self._draw_radar(cx, dashboard_y - 20, 60, enemies, player_pos, player_yaw)

        # 5. Cockpit Struts
        self._draw_cockpit_struts(cx, cy, self.width, self.height)

        # End rotation block (and Sway block)
        glPopMatrix()

        # 3. Center Reticle (Draw AFTER rotation/sway so it stays fixed in center)
        # Re-set color to HUD cyan
        glColor4f(*hud_color)
        self._draw_reticle(cx, cy)

        # --- Render STATIC Text Elements ---
        # Lives (Left side) - as blocks
        self._draw_life_blocks(50, self.height - 50, lives)

        # self._render_text(f"LIVES: {lives}", 50, self.height - 50, self.font)

        # Score (Right side)
        self._render_text(f"SCORE: {score}", self.width - 200, self.height - 50, self.font)

        if fps > 0:
            self._render_text(f"FPS: {fps}", self.width - 100, 20, self.small_font)

        # Re-enable depth test
        glEnable(GL_DEPTH_TEST)

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def _draw_reticle(self, cx, cy):
        """Draw 3-prong reticle"""
        gap = 10
        length = 20

        glLineWidth(2.0)
        glBegin(GL_LINES)

        # Top prong
        glVertex2f(cx, cy + gap)
        glVertex2f(cx, cy + gap + length)

        # Bottom Left prong (210 degrees)
        # cos(210) = -0.866, sin(210) = -0.5
        glVertex2f(cx + bg_cos(210) * gap, cy + bg_sin(210) * gap)
        glVertex2f(cx + bg_cos(210) * (gap + length), cy + bg_sin(210) * (gap + length))

        # Bottom Right prong (330 degrees)
        # cos(330) = 0.866, sin(330) = -0.5
        glVertex2f(cx + bg_cos(330) * gap, cy + bg_sin(330) * gap)
        glVertex2f(cx + bg_cos(330) * (gap + length), cy + bg_sin(330) * (gap + length))

        glEnd()

        # Center dot
        glPointSize(2.0)
        glBegin(GL_POINTS)
        glVertex2f(cx, cy)
        glEnd()
        glPointSize(1.0)
        glLineWidth(1.0)

    def _draw_cockpit_struts(self, cx, cy, w, h):
        """Draw heavy wireframe cockpit pillars"""
        glLineWidth(3.0)

        # Color for struts (Metallic Grey/Blue)
        glColor4f(0.4, 0.4, 0.5, 0.8)

        # Left Strut
        glBegin(GL_LINE_LOOP)
        glVertex2f(0, 0)  # Bottom Left Screen
        glVertex2f(w * 0.2, h * 0.4)  # Mid-left inner
        glVertex2f(w * 0.1, h * 0.9)  # Top-left inner
        glVertex2f(0, h)  # Top Left Screen
        glEnd()

        # Right Strut
        glBegin(GL_LINE_LOOP)
        glVertex2f(w, 0)  # Bottom Right Screen
        glVertex2f(w * 0.8, h * 0.4)  # Mid-right inner
        glVertex2f(w * 0.9, h * 0.9)  # Top-right inner
        glVertex2f(w, h)  # Top Right Screen
        glEnd()

        # Restore HUD color
        glColor4f(0.2, 0.8, 1.0, 0.8)
        glLineWidth(1.0)

    def _draw_radar(self, cx, cy, radius, enemies, player_pos, player_yaw):
        """Draw tactical radar showing enemies"""
        if not enemies or not player_pos:
            return

        # Radar Background (Semi-transparent)
        glColor4f(0.0, 0.1, 0.2, 0.5)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for i in range(361):
            theta = math.radians(i)
            glVertex2f(cx + math.cos(theta) * radius, cy + math.sin(theta) * radius)
        glEnd()

        # Radar Rings
        glColor4f(0.2, 0.8, 1.0, 0.5)
        self._draw_arc(cx, cy, radius, 0, 360, 2.0)
        self._draw_arc(cx, cy, radius * 0.5, 0, 360, 1.0)

        # Crosshairs
        glBegin(GL_LINES)
        glVertex2f(cx - radius, cy)
        glVertex2f(cx + radius, cy)
        glVertex2f(cx, cy - radius)
        glVertex2f(cx, cy + radius)
        glEnd()

        # Player Marker (Center)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_TRIANGLES)
        glVertex2f(cx, cy + 4)
        glVertex2f(cx - 3, cy - 3)
        glVertex2f(cx + 3, cy - 3)
        glEnd()

        # Enemy Blips
        radar_range = 100.0  # Detection range

        # Pre-calculate player direction vectors (2D XZ plane)
        rad_yaw = math.radians(player_yaw)

        # Front vector (based on yaw)
        fx = math.cos(rad_yaw)
        fz = math.sin(rad_yaw)

        # Right vector (front rotated 90 degrees CCW? No, let's verify standard math)
        # If Yaw -90 is Front (0, -1).
        # We want Right to be (1, 0).
        # -90 + 90 = 0. cos(0)=1, sin(0)=0. So Yaw + 90 works.
        rad_right = math.radians(player_yaw + 90)
        rx = math.cos(rad_right)
        rz = math.sin(rad_right)

        glPointSize(3.0)
        glBegin(GL_POINTS)

        for enemy in enemies:
            # Relative position vector
            dx = enemy.position.x - player_pos.x
            dz = enemy.position.z - player_pos.z

            # Simple distance check
            dist = math.sqrt(dx * dx + dz * dz)
            if dist > radar_range:
                continue

            # Project relative position onto Player's Right and Front vectors
            # Radar X = dot(relative, right)
            # Radar Y = dot(relative, front)

            radar_x_proj = dx * rx + dz * rz
            radar_y_proj = dx * fx + dz * fz

            # Map to radar radius
            scale = radius / radar_range
            radar_draw_x = cx + radar_x_proj * scale
            radar_draw_y = cy + radar_y_proj * scale

            glColor4f(1.0, 0.2, 0.2, 1.0)  # Red for enemies
            glVertex2f(radar_draw_x, radar_draw_y)

        glEnd()
        glPointSize(1.0)

    def _draw_arc(self, cx, cy, radius, start_angle, end_angle, thickness):
        """Draw a wireframe arc"""
        glLineWidth(thickness)
        glBegin(GL_LINE_STRIP)

        num_segments = 50
        # Convert to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        for i in range(num_segments + 1):
            theta = start_rad + (end_rad - start_rad) * i / num_segments
            x = cx + math.cos(theta) * radius
            y = cy + math.sin(theta) * radius
            glVertex2f(x, y)

        glEnd()
        glLineWidth(1.0)

    def _draw_ticks_on_arc(self, cx, cy, radius, start_angle, end_angle, num_ticks, length):
        """Draw tick marks along an arc"""
        glLineWidth(2.0)
        glBegin(GL_LINES)

        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        for i in range(num_ticks):
            theta = start_rad + (end_rad - start_rad) * i / (num_ticks - 1)
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)

            # Inner point
            x1 = cx + cos_t * radius
            y1 = cy + sin_t * radius

            # Outer point
            x2 = cx + cos_t * (radius + length)
            y2 = cy + sin_t * (radius + length)

            glVertex2f(x1, y1)
            glVertex2f(x2, y2)

        glEnd()
        glLineWidth(1.0)

    def _draw_triangle_reticle(self, cx, cy, size):
        """Draw a triangle reticle facing center (or outward)"""
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        # Top point
        glVertex2f(cx, cy + size)
        # Bottom Right
        glVertex2f(cx + size * 0.8, cy - size * 0.5)
        # Bottom Left
        glVertex2f(cx - size * 0.8, cy - size * 0.5)
        glEnd()

        # Center dot
        glPointSize(4.0)
        glBegin(GL_POINTS)
        glVertex2f(cx, cy)
        glEnd()
        glPointSize(1.0)

    def _draw_dashboard(self, cx, top_y, radius):
        """Draw wireframe dashboard/nose at bottom"""
        glLineWidth(2.0)
        glBegin(GL_LINE_STRIP)

        # Trapezoid shape at bottom
        # Bottom left
        glVertex2f(cx - radius * 0.6, 0)
        # Top left of dash
        glVertex2f(cx - radius * 0.4, top_y)
        # Top right of dash
        glVertex2f(cx + radius * 0.4, top_y)
        # Bottom right
        glVertex2f(cx + radius * 0.6, 0)

        glEnd()

        # Internal lines
        glBegin(GL_LINES)
        glVertex2f(cx, 0)
        glVertex2f(cx, top_y)
        glEnd()

        glLineWidth(1.0)

    def _draw_life_blocks(self, x, y, lives):
        """Draw life indicators as blocks"""
        block_w = 25
        block_h = 10
        spacing = 5

        # Color based on lives
        if lives <= 1:
            glColor4f(1.0, 0.2, 0.2, 0.8)  # Red Warning
        else:
            glColor4f(0.2, 0.8, 1.0, 0.8)  # HUD Cyan

        glBegin(GL_QUADS)
        for i in range(lives):
            bx = x + i * (block_w + spacing)
            by = y
            glVertex2f(bx, by)
            glVertex2f(bx + block_w, by)
            glVertex2f(bx + block_w, by + block_h)
            glVertex2f(bx, by + block_h)
        glEnd()

    def _render_text(self, text, x, y, font):
        """
        Render text on screen using pygame font

        Args:
            text: Text to render
            x, y: Screen position (bottom-left origin)
            font: Pygame font object
        """
        # Render text to a surface
        text_surface = font.render(text, True, (200, 240, 255))  # Light blue text
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        text_width, text_height = text_surface.get_size()

        # Save current state
        glPushAttrib(GL_ENABLE_BIT)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Create texture from text
        glRasterPos2f(x, y)
        glDrawPixels(text_width, text_height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        # Restore state
        glPopAttrib()

    def render_game_over(self, final_score):
        """
        Render game over screen

        Args:
            final_score: Final score
        """
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        # Draw semi-transparent overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        glDisable(GL_BLEND)

        # Render game over text
        large_font = pygame.font.Font(None, 72)
        self._render_text("GAME OVER", self.width // 2 - 150, self.height // 2 + 50, large_font)
        self._render_text(
            f"Final Score: {final_score}", self.width // 2 - 80, self.height // 2 - 20, self.font
        )
        self._render_text(
            "Press R to Restart or ESC to Quit",
            self.width // 2 - 120,
            self.height // 2 - 80,
            self.small_font,
        )

        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def render_pause(self):
        """Render pause screen"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        # Draw overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        glDisable(GL_BLEND)

        large_font = pygame.font.Font(None, 72)
        self._render_text("PAUSED", self.width // 2 - 100, self.height // 2 + 20, large_font)
        self._render_text(
            "Press ESC to Resume", self.width // 2 - 90, self.height // 2 - 40, self.small_font
        )

        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def resize(self, width, height):
        """Handle window resize"""
        self.width = width
        self.height = height


def bg_cos(deg):
    return math.cos(math.radians(deg))


def bg_sin(deg):
    return math.sin(math.radians(deg))
