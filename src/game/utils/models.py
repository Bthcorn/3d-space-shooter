"""3D model definitions — wireframe AND solid geometry.

SolidModel stores triangulated faces with per-face normals so that
OpenGL fixed-pipeline lighting works correctly.
"""

import math
import numpy as np


# ============================================================
# Wireframe model (kept for backward compat)
# ============================================================

class WireframeModel:
    """Wireframe model: vertices + edge pairs."""

    def __init__(self, vertices, edges):
        self.vertices = np.array(vertices, dtype=np.float32)
        self.edges = edges


# ============================================================
# Solid model
# ============================================================

class SolidModel:
    """Solid model with triangulated faces and per-face normals.

    Attributes:
        vertices:  list of (x, y, z) tuples
        faces:     list of face tuples; each face is a tuple of vertex indices
                   (3 = triangle, 4 = quad)
        normals:   list of (nx, ny, nz) per face, computed automatically.
    """

    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces
        self.normals = self._compute_normals()

    def _compute_normals(self):
        """Compute one outward normal per face."""
        normals = []
        for face in self.faces:
            v0 = np.array(self.vertices[face[0]])
            v1 = np.array(self.vertices[face[1]])
            v2 = np.array(self.vertices[face[2]])
            edge1 = v1 - v0
            edge2 = v2 - v0
            n = np.cross(edge1, edge2)
            length = np.linalg.norm(n)
            if length > 1e-8:
                n = n / length
            else:
                n = np.array([0.0, 1.0, 0.0])
            normals.append(tuple(n))
        return normals


# ============================================================
# Primitive generators
# ============================================================

def create_box(sx=1.0, sy=1.0, sz=1.0):
    """Axis-aligned box centred at origin. Returns SolidModel."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = [
        (-hx, -hy,  hz),  # 0 front-bottom-left
        ( hx, -hy,  hz),  # 1 front-bottom-right
        ( hx,  hy,  hz),  # 2 front-top-right
        (-hx,  hy,  hz),  # 3 front-top-left
        (-hx, -hy, -hz),  # 4 back-bottom-left
        ( hx, -hy, -hz),  # 5 back-bottom-right
        ( hx,  hy, -hz),  # 6 back-top-right
        (-hx,  hy, -hz),  # 7 back-top-left
    ]
    # Quads (4 indices each) — winding order gives outward normals
    faces = [
        (0, 1, 2, 3),  # front  +Z
        (5, 4, 7, 6),  # back   -Z
        (4, 0, 3, 7),  # left   -X
        (1, 5, 6, 2),  # right  +X
        (3, 2, 6, 7),  # top    +Y
        (4, 5, 1, 0),  # bottom -Y
    ]
    return SolidModel(v, faces)


def create_sphere(radius=1.0, slices=14, stacks=10):
    """UV sphere centred at origin. Returns SolidModel with quad faces."""
    verts = []
    faces = []

    for i in range(stacks + 1):
        phi = math.pi * i / stacks  # 0 .. pi
        for j in range(slices + 1):
            theta = 2.0 * math.pi * j / slices  # 0 .. 2pi
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.cos(phi)
            z = radius * math.sin(phi) * math.sin(theta)
            verts.append((x, y, z))

    for i in range(stacks):
        for j in range(slices):
            a = i * (slices + 1) + j
            b = a + 1
            c = a + (slices + 1)
            d = c + 1
            # Two triangles per grid cell
            faces.append((a, c, d))
            faces.append((a, d, b))

    return SolidModel(verts, faces)


def create_pyramid(base=2.0, height=2.0):
    """4-sided pyramid, base on XZ plane, apex at +Y. Returns SolidModel."""
    hb = base / 2
    v = [
        (-hb, 0,  hb),  # 0 front-left
        ( hb, 0,  hb),  # 1 front-right
        ( hb, 0, -hb),  # 2 back-right
        (-hb, 0, -hb),  # 3 back-left
        (0, height, 0), # 4 apex
    ]
    faces = [
        (0, 1, 4),  # front
        (1, 2, 4),  # right
        (2, 3, 4),  # back
        (3, 0, 4),  # left
        (0, 3, 2, 1),  # base (bottom)
    ]
    return SolidModel(v, faces)


def create_elongated_box(length=3.0, width=1.0, height=0.6):
    """Ship-like elongated box. Nose at +Z."""
    return create_box(width, height, length)


def create_diamond(radius=1.0, height=2.0):
    """Octahedron-like diamond shape. Returns SolidModel."""
    hh = height / 2
    v = [
        ( radius, 0, 0),   # 0
        ( 0, 0, radius),   # 1
        (-radius, 0, 0),   # 2
        ( 0, 0, -radius),  # 3
        ( 0, hh, 0),       # 4 top
        ( 0, -hh, 0),      # 5 bottom
    ]
    faces = [
        # Top 4 triangles
        (0, 1, 4),
        (1, 2, 4),
        (2, 3, 4),
        (3, 0, 4),
        # Bottom 4 triangles
        (1, 0, 5),
        (2, 1, 5),
        (3, 2, 5),
        (0, 3, 5),
    ]
    return SolidModel(v, faces)


def create_cone(radius=1.0, height=2.0, segments=12):
    """Cone with base on XZ plane, apex at +Y."""
    verts = [(0, height, 0)]  # apex = index 0
    verts.append((0, 0, 0))   # center of base = index 1

    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        verts.append((x, 0, z))

    faces = []
    for i in range(segments):
        curr = i + 2
        nxt = ((i + 1) % segments) + 2
        # Side triangle
        faces.append((0, nxt, curr))
        # Base triangle
        faces.append((1, curr, nxt))

    return SolidModel(verts, faces)


# ============================================================
# Game-specific model factories
# ============================================================

def create_player_ship_solid():
    """Solid player ship — angular fighter shape."""
    v = [
        (0, 0, 2.0),        # 0 nose
        (-1.0, -0.3, -0.5), # 1 body BL
        (1.0, -0.3, -0.5),  # 2 body BR
        (1.0, 0.3, -0.5),   # 3 body TR
        (-1.0, 0.3, -0.5),  # 4 body TL
        (-0.8, -0.2, -1.8), # 5 rear BL
        (0.8, -0.2, -1.8),  # 6 rear BR
        (0.8, 0.2, -1.8),   # 7 rear TR
        (-0.8, 0.2, -1.8),  # 8 rear TL
        (-2.5, -0.1, -1.0), # 9 left wing tip
        (2.5, -0.1, -1.0),  # 10 right wing tip
        (0, 0.6, -0.2),     # 11 cockpit top
    ]
    faces = [
        # Nose triangles
        (0, 2, 1),  # bottom
        (0, 3, 2),  # right
        (0, 4, 3),  # top
        (0, 1, 4),  # left
        # Body sides (quads)
        (1, 2, 6, 5),  # bottom
        (2, 3, 7, 6),  # right
        (3, 4, 8, 7),  # top
        (4, 1, 5, 8),  # left
        # Rear face
        (5, 6, 7, 8),
        # Left wing
        (1, 9, 5),
        (1, 4, 9),
        (4, 8, 9),
        (9, 8, 5),
        # Right wing
        (2, 6, 10),
        (2, 10, 3),
        (3, 10, 7),
        (10, 6, 7),
        # Cockpit
        (0, 3, 11),
        (0, 11, 4),
        (3, 4, 11),
    ]
    return SolidModel(v, faces)


def create_enemy_standard_solid():
    """Solid standard enemy — chunky fighter."""
    v = [
        (0, 0, 1.8),        # 0 nose
        (-0.6, 0.35, -0.2), # 1
        (0.6, 0.35, -0.2),  # 2
        (0.6, -0.35, -0.2), # 3
        (-0.6, -0.35, -0.2),# 4
        (-0.5, 0.3, -1.2),  # 5
        (0.5, 0.3, -1.2),   # 6
        (0.5, -0.3, -1.2),  # 7
        (-0.5, -0.3, -1.2), # 8
        (0, 0, -1.5),       # 9 tail
    ]
    faces = [
        (0, 2, 1), (0, 3, 2), (0, 4, 3), (0, 1, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 4, 8, 7), (4, 1, 5, 8),
        (9, 5, 6), (9, 6, 7), (9, 7, 8), (9, 8, 5),
    ]
    return SolidModel(v, faces)


def create_enemy_heavy_solid():
    """Solid heavy enemy — bulky."""
    v = [
        (-0.5, 0.5, 1), (0.5, 0.5, 1), (0.5, -0.5, 1), (-0.5, -0.5, 1),
        (-0.8, 0.8, -1), (0.8, 0.8, -1), (0.8, -0.8, -1), (-0.8, -0.8, -1),
        (0, 0, 1.5),
    ]
    faces = [
        (0, 1, 2, 3),
        (5, 4, 7, 6),
        (4, 0, 3, 7), (1, 5, 6, 2),
        (4, 5, 1, 0), (3, 2, 6, 7),
        (8, 1, 0), (8, 2, 1), (8, 3, 2), (8, 0, 3),
    ]
    return SolidModel(v, faces)


def create_enemy_interceptor_solid():
    """Solid interceptor — sleek."""
    v = [
        (0, 0, 1.5),        # 0 nose
        (-0.3, 0.15, 0.3),  # 1
        (0.3, 0.15, 0.3),   # 2
        (0.3, -0.15, 0.3),  # 3
        (-0.3, -0.15, 0.3), # 4
        (-1.4, 0, 0.8),     # 5 left wing
        (1.4, 0, 0.8),      # 6 right wing
        (-0.4, 0, -1.0),    # 7 rear left
        (0.4, 0, -1.0),     # 8 rear right
        (0, 0, -1.2),       # 9 engine
    ]
    faces = [
        (0, 2, 1), (0, 3, 2), (0, 4, 3), (0, 1, 4),
        (1, 5, 4), (5, 7, 4), (4, 7, 3),
        (2, 3, 6), (3, 8, 6), (6, 8, 2),
        (1, 7, 5), (2, 8, 3),
        (7, 9, 8), (7, 8, 3, 4),
    ]
    return SolidModel(v, faces)


def create_meteorite_solid(size=1.0):
    """Irregular-ish rock shape based on a deformed sphere."""
    import random as _r
    _r.seed(42)  # Deterministic shape
    base = create_sphere(radius=size, slices=8, stacks=6)
    # Deform vertices slightly
    deformed = []
    for v in base.vertices:
        factor = 0.8 + _r.random() * 0.4  # 0.8 – 1.2
        deformed.append((v[0] * factor, v[1] * factor, v[2] * factor))
    return SolidModel(deformed, base.faces)


def create_life_sphere_solid(radius=1.0):
    """Sphere for the life pickup."""
    return create_sphere(radius=radius, slices=12, stacks=8)


def create_laser_solid(length=2.0, radius=0.08, segments=16):
    """Cylindrical laser bolt aligned along +Z."""
    import math

    half = length / 2.0

    # Two rings of vertices: front (+Z) and back (-Z)
    verts = []
    for ring_z in (half, -half):
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            verts.append((x, y, ring_z))

    faces = []
    # Side quads between the two rings
    for i in range(segments):
        i0 = i
        i1 = (i + 1) % segments
        i2 = i1 + segments
        i3 = i + segments
        faces.append((i0, i1, i2, i3))

    # Optional end caps (front and back) as triangles
    center_front = len(verts)
    center_back = len(verts) + 1
    verts.append((0.0, 0.0, half))
    verts.append((0.0, 0.0, -half))

    for i in range(segments):
        i0 = i
        i1 = (i + 1) % segments
        faces.append((center_front, i1, i0))

    for i in range(segments):
        i0 = segments + i
        i1 = segments + (i + 1) % segments
        faces.append((center_back, i0, i1))

    return SolidModel(verts, faces)




# ============================================================
# Wireframe models (original, for backward compat)
# ============================================================

def create_player_ship():
    """Create player spaceship wireframe."""
    vertices = [
        (0, 0, 2), (-1, -0.5, 0), (1, -0.5, 0), (1, 0.5, 0), (-1, 0.5, 0),
        (-1, -0.5, -2), (1, -0.5, -2), (1, 0.5, -2), (-1, 0.5, -2),
        (-3, -0.5, -1), (3, -0.5, -1), (0, 1, 0.5),
    ]
    edges = [
        (0,1),(0,2),(0,3),(0,4),(1,2),(2,3),(3,4),(4,1),
        (1,5),(2,6),(3,7),(4,8),(5,6),(6,7),(7,8),(8,5),
        (1,9),(5,9),(2,10),(6,10),(3,11),(4,11),(11,0),
    ]
    return WireframeModel(vertices, edges)


class EnemyModelFactory:
    """Factory for enemy ship models."""

    _builders = None

    @classmethod
    def _ensure_builders(cls):
        if cls._builders is None:
            cls._builders = [
                cls.create_standard,
                cls.create_heavy,
                cls.create_interceptor,
                cls.create_scout,
                cls.create_stealth,
                cls.create_assault,
            ]

    @classmethod
    def get_random_builder(cls):
        cls._ensure_builders()
        import random
        return random.choice(cls._builders)

    # --- Solid builders used by new renderer ---
    _solid_builders = None

    @classmethod
    def _ensure_solid_builders(cls):
        if cls._solid_builders is None:
            cls._solid_builders = [
                create_enemy_standard_solid,
                create_enemy_heavy_solid,
                create_enemy_interceptor_solid,
            ]

    @classmethod
    def get_random_solid(cls):
        cls._ensure_solid_builders()
        import random
        return random.choice(cls._solid_builders)()

    # --- Original wireframe builders (kept) ---

    @staticmethod
    def create_standard():
        v = [
            (0,0,2.0),(-0.7,0.4,0),(0.7,0.4,0),(0.7,0.4,-0.5),(-0.7,0.4,-0.5),
            (-0.7,-0.4,0),(0.7,-0.4,0),(0.7,-0.4,-0.5),(-0.7,-0.4,-0.5),
            (-0.5,0.3,-1.2),(0.5,0.3,-1.2),(0.5,-0.3,-1.2),(-0.5,-0.3,-1.2),(0,0,-2.0),
        ]
        edges = [
            (0,1),(0,2),(0,5),(0,6),(1,2),(2,3),(3,4),(4,1),(5,6),(6,7),(7,8),(8,5),
            (1,5),(2,6),(3,7),(4,8),(4,9),(3,10),(7,11),(8,12),
            (9,10),(10,11),(11,12),(12,9),(13,9),(13,10),(13,11),(13,12),
        ]
        return WireframeModel(v, edges)

    @staticmethod
    def create_heavy():
        v = [
            (-0.5,0.5,1),(0.5,0.5,1),(0.5,-0.5,1),(-0.5,-0.5,1),
            (-0.8,0.8,-1),(0.8,0.8,-1),(0.8,-0.8,-1),(-0.8,-0.8,-1),(0,0,1.5),
        ]
        edges = [
            (0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7),(8,0),(8,1),(8,2),(8,3),
        ]
        return WireframeModel(v, edges)

    @staticmethod
    def create_interceptor():
        v = [
            (0,0,1.5),(-0.3,0,0.5),(0.3,0,0.5),(0,0.2,0.5),(0,-0.2,0.5),
            (-1.5,0,1.0),(1.5,0,1.0),(-0.5,0,-1.0),(0.5,0,-1.0),(0,0,-1.2),
        ]
        edges = [
            (0,1),(0,2),(0,3),(0,4),(1,2),(3,4),(1,3),(2,4),(2,3),
            (1,5),(5,7),(2,6),(6,8),(7,8),(7,9),(8,9),(1,7),(2,8),
        ]
        return WireframeModel(v, edges)

    @staticmethod
    def create_scout():
        v = [
            (0,0,1.2),(-1.0,0.2,-0.5),(1.0,0.2,-0.5),
            (-1.0,-0.2,-0.5),(1.0,-0.2,-0.5),
            (0,0.5,-0.5),(0,-0.5,-0.5),(0,0,-0.5),
        ]
        edges = [
            (0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
            (1,3),(2,4),(1,2),(3,4),(5,6),
            (1,5),(2,5),(3,6),(4,6),(5,7),(6,7),(1,7),(2,7),(3,7),(4,7),
        ]
        return WireframeModel(v, edges)

    @staticmethod
    def create_stealth():
        v = [(0,0,1.5),(-1.2,0,-0.5),(1.2,0,-0.5),(0,0.2,-0.5),(0,-0.2,-0.5)]
        edges = [(0,1),(1,3),(3,2),(2,0),(1,4),(4,2),(0,3),(0,4),(3,4)]
        return WireframeModel(v, edges)

    @staticmethod
    def create_assault():
        v = [
            (-0.8,-0.2,1),(-0.4,-0.2,1),(-0.4,0.2,1),(-0.8,0.2,1),
            (-0.8,-0.2,-1),(-0.4,-0.2,-1),(-0.4,0.2,-1),(-0.8,0.2,-1),
            (0.4,-0.2,1),(0.8,-0.2,1),(0.8,0.2,1),(0.4,0.2,1),
            (0.4,-0.2,-1),(0.8,-0.2,-1),(0.8,0.2,-1),(0.4,0.2,-1),
            (-0.4,0,0),(0.4,0,0),
        ]
        edges = [
            (0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
            (0,4),(1,5),(2,6),(3,7),
            (8,9),(9,10),(10,11),(11,8),(12,13),(13,14),(14,15),(15,12),
            (8,12),(9,13),(10,14),(11,15),(16,17),
        ]
        return WireframeModel(v, edges)
