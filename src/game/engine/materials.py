"""Material system for OpenGL fixed pipeline.

Each material is a dictionary with ambient, diffuse, specular, shininess,
and alpha values.  apply_material() pushes them to the GL state.
"""

from OpenGL.GL import *


# ---------- helper ----------------------------------------------------------

def apply_material(mat):
    """Apply a material dictionary to the current OpenGL state.

    Args:
        mat: dict with keys 'ambient', 'diffuse', 'specular', 'shininess',
             and optionally 'alpha' (default 1.0), 'emission' (default black).
    """
    alpha = mat.get("alpha", 1.0)
    face = GL_FRONT_AND_BACK

    amb = mat["ambient"]
    diff = mat["diffuse"]
    spec = mat["specular"]
    shin = mat["shininess"]
    emit = mat.get("emission", (0.0, 0.0, 0.0, 1.0))

    # Inject alpha into diffuse so blending works
    glMaterialfv(face, GL_AMBIENT, (amb[0], amb[1], amb[2], alpha))
    glMaterialfv(face, GL_DIFFUSE, (diff[0], diff[1], diff[2], alpha))
    glMaterialfv(face, GL_SPECULAR, (spec[0], spec[1], spec[2], 1.0))
    glMaterialf(face, GL_SHININESS, shin)
    glMaterialfv(face, GL_EMISSION, emit)


def apply_material_scaled(mat, brightness=1.0):
    """Apply material with diffuse scaled by brightness (for day/night)."""
    alpha = mat.get("alpha", 1.0)
    face = GL_FRONT_AND_BACK
    b = max(0.0, min(brightness, 1.0))

    amb = mat["ambient"]
    diff = mat["diffuse"]
    spec = mat["specular"]
    shin = mat["shininess"]
    emit = mat.get("emission", (0.0, 0.0, 0.0, 1.0))

    glMaterialfv(face, GL_AMBIENT, (amb[0] * b, amb[1] * b, amb[2] * b, alpha))
    glMaterialfv(face, GL_DIFFUSE, (diff[0], diff[1], diff[2], alpha))
    glMaterialfv(face, GL_SPECULAR, (spec[0], spec[1], spec[2], 1.0))
    glMaterialf(face, GL_SHININESS, shin)
    glMaterialfv(face, GL_EMISSION, emit)


# ============================================================
# Pre-defined materials
# ============================================================

# --- A) Opaque matte (low specular, low shininess) -------------------------
MATERIAL_MATTE_GRAY = {
    "ambient":   (0.15, 0.15, 0.15, 1.0),
    "diffuse":   (0.55, 0.55, 0.55, 1.0),
    "specular":  (0.1, 0.1, 0.1, 1.0),
    "shininess": 5.0,
    "alpha":     1.0,
}

MATERIAL_MATTE_RED = {
    "ambient":   (0.2, 0.04, 0.04, 1.0),
    "diffuse":   (0.8, 0.15, 0.15, 1.0),
    "specular":  (0.1, 0.05, 0.05, 1.0),
    "shininess": 8.0,
    "alpha":     1.0,
}

MATERIAL_MATTE_GREEN = {
    "ambient":   (0.04, 0.18, 0.04, 1.0),
    "diffuse":   (0.15, 0.75, 0.15, 1.0),
    "specular":  (0.05, 0.1, 0.05, 1.0),
    "shininess": 8.0,
    "alpha":     1.0,
}

# --- B) Opaque glossy / metallic (high specular + shininess) ----------------
MATERIAL_METAL_SILVER = {
    "ambient":   (0.19, 0.19, 0.19, 1.0),
    "diffuse":   (0.51, 0.51, 0.51, 1.0),
    "specular":  (0.77, 0.77, 0.77, 1.0),
    "shininess": 90.0,
    "alpha":     1.0,
}

MATERIAL_METAL_GOLD = {
    "ambient":   (0.25, 0.20, 0.07, 1.0),
    "diffuse":   (0.75, 0.61, 0.23, 1.0),
    "specular":  (0.95, 0.85, 0.45, 1.0),
    "shininess": 80.0,
    "alpha":     1.0,
}

MATERIAL_GLOSSY_RED = {
    "ambient":   (0.18, 0.02, 0.02, 1.0),
    "diffuse":   (0.85, 0.10, 0.10, 1.0),
    "specular":  (0.90, 0.70, 0.70, 1.0),
    "shininess": 70.0,
    "alpha":     1.0,
}

MATERIAL_GLOSSY_ORANGE = {
    "ambient":   (0.20, 0.10, 0.02, 1.0),
    "diffuse":   (0.90, 0.45, 0.05, 1.0),
    "specular":  (0.95, 0.75, 0.50, 1.0),
    "shininess": 65.0,
    "alpha":     1.0,
}

MATERIAL_GLOSSY_PURPLE = {
    "ambient":   (0.12, 0.02, 0.18, 1.0),
    "diffuse":   (0.55, 0.10, 0.85, 1.0),
    "specular":  (0.80, 0.60, 0.95, 1.0),
    "shininess": 72.0,
    "alpha":     1.0,
}

MATERIAL_GLOSSY_YELLOW = {
    "ambient":   (0.20, 0.18, 0.02, 1.0),
    "diffuse":   (0.95, 0.85, 0.10, 1.0),
    "specular":  (1.00, 0.95, 0.60, 1.0),
    "shininess": 68.0,
    "alpha":     1.0,
}

MATERIAL_GLOSSY_CYAN = {
    "ambient":   (0.02, 0.14, 0.18, 1.0),
    "diffuse":   (0.10, 0.70, 0.85, 1.0),
    "specular":  (0.60, 0.90, 0.95, 1.0),
    "shininess": 75.0,
    "alpha":     1.0,
}

MATERIAL_GLOSSY_PINK = {
    "ambient":   (0.18, 0.04, 0.10, 1.0),
    "diffuse":   (0.90, 0.20, 0.55, 1.0),
    "specular":  (0.95, 0.65, 0.80, 1.0),
    "shininess": 70.0,
    "alpha":     1.0,
}

# Pool of enemy materials for random assignment
ENEMY_MATERIAL_POOL = [
    MATERIAL_GLOSSY_RED,
    MATERIAL_GLOSSY_ORANGE,
    MATERIAL_GLOSSY_PURPLE,
    MATERIAL_GLOSSY_YELLOW,
    MATERIAL_GLOSSY_CYAN,
    MATERIAL_GLOSSY_PINK,
    MATERIAL_METAL_GOLD,
]

# --- C) Transparent / glass (alpha < 1) ------------------------------------
MATERIAL_GLASS_CYAN = {
    "ambient":   (0.05, 0.15, 0.18, 1.0),
    "diffuse":   (0.1, 0.5, 0.6, 1.0),
    "specular":  (0.9, 0.9, 0.95, 1.0),
    "shininess": 100.0,
    "alpha":     0.35,
}

MATERIAL_GLASS_GREEN = {
    "ambient":   (0.02, 0.12, 0.02, 1.0),
    "diffuse":   (0.1, 0.6, 0.1, 1.0),
    "specular":  (0.85, 0.95, 0.85, 1.0),
    "shininess": 96.0,
    "alpha":     0.30,
}


# --- Extra: emissive laser materials ---------------------------------------
MATERIAL_LASER_GREEN = {
    "ambient":   (0.0, 0.2, 0.0, 1.0),
    "diffuse":   (0.0, 0.5, 0.0, 1.0),
    "specular":  (0.3, 0.8, 0.3, 1.0),
    "shininess": 50.0,
    "alpha":     0.85,
    "emission":  (0.0, 0.9, 0.0, 1.0),
}

MATERIAL_LASER_RED = {
    "ambient":   (0.2, 0.0, 0.0, 1.0),
    "diffuse":   (0.5, 0.0, 0.0, 1.0),
    "specular":  (0.8, 0.3, 0.3, 1.0),
    "shininess": 50.0,
    "alpha":     0.85,
    "emission":  (0.9, 0.0, 0.0, 1.0),
}

# --- Extra: life sphere (glowing cyan, slightly transparent) ----------------
MATERIAL_LIFE_SPHERE = {
    "ambient":   (0.0, 0.15, 0.15, 1.0),
    "diffuse":   (0.0, 0.7, 0.7, 1.0),
    "specular":  (0.8, 1.0, 1.0, 1.0),
    "shininess": 96.0,
    "alpha":     0.55,
    "emission":  (0.0, 0.25, 0.25, 1.0),
}


# --- Explosion material: bright, light, semi-transparent --------------------
MATERIAL_EXPLOSION = {
    # Lighter yellow-orange base
    "ambient":   (0.6, 0.4, 0.1, 1.0),
    "diffuse":   (1.0, 0.85, 0.4, 1.0),
    "specular":  (1.0, 0.9, 0.6, 1.0),
    "shininess": 40.0,
    # More transparent to get a lighter, airy look
    "alpha":     0.45,
    # Strong, almost white-hot emission
    "emission":  (1.0, 0.9, 0.7, 1.0),
}
