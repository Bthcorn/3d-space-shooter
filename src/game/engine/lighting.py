"""Day / Night lighting system.

Design
------
A single continuous parameter  t ∈ [0..1]  is derived from a cosine wave:

    t = (1 − cos(2π · time)) / 2

  t = 0  →  midnight    t = 1  →  noon

Every frame, exactly THREE visual parameters are updated by lerping between
their night (t=0) and day (t=1) endpoints using that same t:

  1. glClearColor          — sky / background colour
  2. GL_LIGHT0 colours     — directional sun (day) ↔ moon (night), same light
  3. GL_LIGHT_MODEL_AMBIENT — global scene brightness / fill light

The system no longer uses a separate flashlight light; visibility is governed
solely by the main directional light and optional night-vision ambient boost.
"""

import math
from OpenGL.GL import *

from game.config import (
    DAY_NIGHT_CYCLE_SPEED,
    SKY_DAY,
    SKY_NIGHT,
    SUN_DIFFUSE,
    SUN_SPECULAR,
    SUN_AMBIENT,
    MOON_DIFFUSE,
    MOON_SPECULAR,
    MOON_AMBIENT,
    GLOBAL_AMBIENT_DAY,
    GLOBAL_AMBIENT_NIGHT,
    LIGHT_ORBIT_RADIUS,
    LIGHT_HEIGHT,
    NIGHT_VISION_AMBIENT,
)


def _lerp4(a, b, t):
    """Component-wise linear interpolation of two 4-tuples."""
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


class LightingSystem:
    """Manages the day/night cycle and optional night-vision ambient boost."""

    def __init__(self):
        # time ∈ [0..1]: 0 = midnight, 0.25 = sunrise, 0.5 = noon, 0.75 = sunset
        self.time = 0.25

        # t ∈ [0..1]: the single smooth parameter that drives the effects
        self.t = self._compute_t(self.time)

        self.night_vision = False

        self._init_opengl_lighting()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_t(time):
        """Map time ∈ [0..1] → smooth day-factor t ∈ [0..1].

        Uses  t = (1 − cos(2π·time)) / 2  so that:
          • t rises smoothly from 0 (midnight) to 1 (noon) and back.
          • The curve has zero first-derivative at both endpoints, giving
            a natural, gradual dawn/dusk instead of a sudden switch.
        """
        return (1.0 - math.cos(2.0 * math.pi * time)) / 2.0

    # ------------------------------------------------------------------
    # OpenGL one-time init
    # ------------------------------------------------------------------

    def _init_opengl_lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)           # Sun / Moon — the ONE cycle-driven light
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(self, dt):
        """Advance the day/night clock and recompute t."""
        self.time = (self.time + DAY_NIGHT_CYCLE_SPEED * dt) % 1.0
        self.t    = self._compute_t(self.time)

    # ------------------------------------------------------------------
    # Per-frame apply  (call AFTER gluLookAt so light positions are correct)
    # ------------------------------------------------------------------

    def apply(self, camera=None):
        """Push all cycle-driven lighting state to OpenGL.

        The three required visual parameters are applied in order:
          1. Background clear colour  (glClearColor)
          2. GL_LIGHT0 intensity      (sun ↔ moon colours)
          3. Global ambient           (scene brightness)
        """
        t = self.t   # single smooth parameter ∈ [0..1]

        # ── 1. Sky / background colour ─────────────────────────────────────
        glClearColor(*_lerp4(SKY_NIGHT, SKY_DAY, t))

        # ── 2. GL_LIGHT0: sun (t=1) ↔ moon (t=0) — same light, lerped ─────
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  _lerp4(MOON_DIFFUSE,  SUN_DIFFUSE,  t))
        glLightfv(GL_LIGHT0, GL_SPECULAR, _lerp4(MOON_SPECULAR, SUN_SPECULAR, t))
        glLightfv(GL_LIGHT0, GL_AMBIENT,  _lerp4(MOON_AMBIENT,  SUN_AMBIENT,  t))

        # Directional light orbits overhead; negative Y = below horizon (night)
        angle = self.time * 2.0 * math.pi
        glLightfv(GL_LIGHT0, GL_POSITION, (
            math.cos(angle) * LIGHT_ORBIT_RADIUS,
            math.sin(angle) * LIGHT_HEIGHT,    # positive = above, negative = below
            math.sin(angle) * LIGHT_ORBIT_RADIUS * 0.3,
            0.0,                               # w=0 → directional light
        ))

        # ── 3. Global ambient — scene brightness fill ──────────────────────
        if self.night_vision:
            # Night-vision overrides the cycle for the ambient only
            glLightModelfv(GL_LIGHT_MODEL_AMBIENT, NIGHT_VISION_AMBIENT)
        else:
            glLightModelfv(GL_LIGHT_MODEL_AMBIENT,
                           _lerp4(GLOBAL_AMBIENT_NIGHT, GLOBAL_AMBIENT_DAY, t))

    # ------------------------------------------------------------------
    # Toggles
    # ------------------------------------------------------------------

    def toggle_night_vision(self):
        self.night_vision = not self.night_vision

    # ------------------------------------------------------------------
    # Queries  (used by HUD and renderer)
    # ------------------------------------------------------------------

    def get_day_factor(self):
        """Return t ∈ [0..1].  0 = full night, 1 = full day."""
        return self.t

    def get_time_of_day_string(self):
        t = self.t
        if t > 0.75:
            return "Day"
        elif t > 0.45:
            return "Sunset" if self.time > 0.5 else "Sunrise"
        elif t > 0.15:
            return "Dusk"   if self.time > 0.5 else "Dawn"
        else:
            return "Night"

    def disable_for_hud(self):
        glDisable(GL_LIGHTING)

    def enable_after_hud(self):
        glEnable(GL_LIGHTING)
