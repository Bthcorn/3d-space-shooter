"""3D Wireframe model definitions"""

import numpy as np


class WireframeModel:
    """Base class for wireframe 3D models"""

    def __init__(self, vertices, edges):
        """
        Args:
            vertices: List of (x, y, z) vertex coordinates
            edges: List of (start_idx, end_idx) vertex index pairs
        """
        self.vertices = np.array(vertices, dtype=np.float32)
        self.edges = edges

    def get_vertex_data(self):
        """Get flat array of vertices"""
        return self.vertices.flatten()

    def get_edge_indices(self):
        """Get flat array of edge indices"""
        return np.array(self.edges, dtype=np.uint32).flatten()


# Spaceship models
def create_player_ship():
    """Create player spaceship wireframe"""
    vertices = [
        # Front nose
        (0, 0, 2),
        # Body
        (-1, -0.5, 0),
        (1, -0.5, 0),
        (1, 0.5, 0),
        (-1, 0.5, 0),
        # Rear
        (-1, -0.5, -2),
        (1, -0.5, -2),
        (1, 0.5, -2),
        (-1, 0.5, -2),
        # Wings
        (-3, -0.5, -1),
        (3, -0.5, -1),
        # Cockpit
        (0, 1, 0.5),
    ]

    edges = [
        # Front to body
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        # Body square
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 1),
        # Body to rear
        (1, 5),
        (2, 6),
        (3, 7),
        (4, 8),
        # Rear square
        (5, 6),
        (6, 7),
        (7, 8),
        (8, 5),
        # Wings
        (1, 9),
        (5, 9),
        (2, 10),
        (6, 10),
        # Cockpit
        (3, 11),
        (4, 11),
        (11, 0),
    ]

    return WireframeModel(vertices, edges)


class EnemyModelFactory:
    """Factory for creating different enemy ship models"""

    @staticmethod
    def create_standard():
        """Create standard enemy ship (original design)"""
        v = [
            # Front Nose
            (0, 0, 2.0),
            # Main Hull - TOP
            (-0.7, 0.4, 0),
            (0.7, 0.4, 0),
            (0.7, 0.4, -0.5),  # Wing top edge
            (-0.7, 0.4, -0.5),
            # Main Hull - BOTTOM
            (-0.7, -0.4, 0),
            (0.7, -0.4, 0),
            (0.7, -0.4, -0.5),
            (-0.7, -0.4, -0.5),
            # Rear Engine Block
            (-0.5, 0.3, -1.2),
            (0.5, 0.3, -1.2),
            (0.5, -0.3, -1.2),
            (-0.5, -0.3, -1.2),
            # Rear Point
            (0, 0, -2.0),
        ]

        vertices = v

        edges = [
            # Nose to Front Hull
            (0, 1),
            (0, 2),
            (0, 5),
            (0, 6),
            # Fuselage (Top/Bottom connection)
            (1, 5),
            (2, 6),
            (3, 7),
            (4, 8),
            # Wings/Side
            (1, 4),
            (4, 3),
            (3, 2),  # Top face
            (5, 8),
            (8, 7),
            (7, 6),  # Bottom face
            # Hull to Engine
            (1, 9),
            (2, 10),
            (5, 12),
            (6, 11),
            # Engine Block
            (9, 10),
            (10, 11),
            (11, 12),
            (12, 9),
            # Engine to Tail
            (9, 13),
            (10, 13),
            (11, 13),
            (12, 13),
        ]

        return WireframeModel(vertices, edges)

    @staticmethod
    def create_scout():
        """Create scout enemy spaceship (fast, light)"""
        # Added vertical volume to body and wings
        vertices = [
            # Front Nose
            (0, 0, 1.2),
            # Wings (now thicker)
            # Top layer
            (-1.0, 0.2, -0.5),
            (1.0, 0.2, -0.5),
            # Bottom layer
            (-1.0, -0.2, -0.5),
            (1.0, -0.2, -0.5),
            # Body rear (thicker vertical fin)
            (0, 0.5, -0.5),  # Top fin
            (0, -0.5, -0.5),  # Bottom fin
            # Rear engine center
            (0, 0, -0.5),
        ]

        edges = [
            # Nose connections
            (0, 1),
            (0, 2),  # Top wings
            (0, 3),
            (0, 4),  # Bottom wings
            (0, 5),
            (0, 6),  # Fins
            # Wing thickness
            (1, 3),
            (2, 4),
            # Rear Structure
            (1, 5),
            (2, 5),  # Top wing-to-fin
            (3, 6),
            (4, 6),  # Bottom wing-to-fin
            # Cross bracing
            (5, 7),
            (6, 7),
            (1, 7),
            (2, 7),
            (3, 7),
            (4, 7),
        ]

        return WireframeModel(vertices, edges)

    @staticmethod
    def create_heavy():
        """Create heavy enemy spaceship (tank-like)"""
        vertices = [
            # Main hull front
            (-0.5, 0.5, 1),
            (0.5, 0.5, 1),
            (0.5, -0.5, 1),
            (-0.5, -0.5, 1),
            # Main hull rear
            (-0.8, 0.8, -1),
            (0.8, 0.8, -1),
            (0.8, -0.8, -1),
            (-0.8, -0.8, -1),
            # Center spike
            (0, 0, 1.5),
        ]

        edges = [
            # Front face
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            # Rear face
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            # Connecting
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
            # Center spike
            (8, 0),
            (8, 1),
            (8, 2),
            (8, 3),
        ]

        return WireframeModel(vertices, edges)

    @staticmethod
    def create_interceptor():
        """Create interceptor enemy (aggressive forward-swept wings)"""
        vertices = [
            # Body
            (0, 0, 1.5),  # Nose
            (-0.3, 0, 0.5),
            (0.3, 0, 0.5),
            (0, 0.2, 0.5),
            (0, -0.2, 0.5),
            # Wings tips (forward swept)
            (-1.5, 0, 1.0),
            (1.5, 0, 1.0),
            # Rear
            (-0.5, 0, -1.0),
            (0.5, 0, -1.0),
            (0, 0, -1.2),  # Engine
        ]

        edges = [
            # Nose cone
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            # Mid body
            (1, 2),
            (3, 4),
            (1, 3),
            (2, 4),
            (2, 3),
            (1, 4),
            # Body to rear
            (1, 7),
            (2, 8),
            (3, 9),
            (4, 9),
            # Wings
            (7, 5),
            (5, 1),  # Left wing
            (8, 6),
            (6, 2),  # Right wing
        ]

        return WireframeModel(vertices, edges)

    @staticmethod
    def create_bomber():
        """Create bomber enemy (wide wingspan, heavy)"""
        vertices = [
            # Center fuselage
            (0, 0, 1.0),
            (-0.5, 0.2, -0.5),
            (0.5, 0.2, -0.5),
            (0.5, -0.2, -0.5),
            (-0.5, -0.2, -0.5),
            # Wings
            (-2.5, 0, -0.5),
            (2.5, 0, -0.5),
            (-2.5, 0, 0),
            (2.5, 0, 0),
        ]

        edges = [
            # Fuselage
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 1),
            # Wings
            (1, 5),
            (5, 7),
            (7, 4),  # Left wing
            (2, 6),
            (6, 8),
            (8, 3),  # Right wing
        ]

        return WireframeModel(vertices, edges)

    @staticmethod
    def create_frigate():
        """Create frigate enemy (vertical structure)"""
        vertices = [
            # Top spike
            (0, 1.5, 0),
            # Top section
            (-0.3, 0.5, 0.3),
            (0.3, 0.5, 0.3),
            (0.3, 0.5, -0.3),
            (-0.3, 0.5, -0.3),
            # Bottom section
            (-0.3, -0.5, 0.3),
            (0.3, -0.5, 0.3),
            (0.3, -0.5, -0.3),
            (-0.3, -0.5, -0.3),
            # Bottom spike
            (0, -1.5, 0),
        ]

        edges = [
            # Top spike
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            # Top ring
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 1),
            # Vertical spars
            (1, 5),
            (2, 6),
            (3, 7),
            (4, 8),
            # Bottom ring
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 5),
            # Bottom spike
            (9, 5),
            (9, 6),
            (9, 7),
            (9, 8),
        ]

        return WireframeModel(vertices, edges)

    @staticmethod
    def create_stealth():
        """Create stealth enemy (flat, triangular)"""
        vertices = [
            # Nose
            (0, 0, 1.5),
            # Rear corners
            (-1.2, 0, -0.5),
            (1.2, 0, -0.5),
            # Top/Bottom mid
            (0, 0.2, -0.5),
            (0, -0.2, -0.5),
        ]

        edges = [
            # Outline
            (0, 1),
            (1, 3),
            (3, 2),
            (2, 0),
            (1, 4),
            (4, 2),
            # Central spine
            (0, 3),
            (0, 4),
            (3, 4),
        ]

        return WireframeModel(vertices, edges)

    @staticmethod
    def create_assault():
        """Create assault enemy (twin-hull/boxy)"""
        vertices = [
            # Left Hull
            (-0.8, -0.2, 1),
            (-0.4, -0.2, 1),
            (-0.4, 0.2, 1),
            (-0.8, 0.2, 1),  # Front
            (-0.8, -0.2, -1),
            (-0.4, -0.2, -1),
            (-0.4, 0.2, -1),
            (-0.8, 0.2, -1),  # Rear
            # Right Hull
            (0.4, -0.2, 1),
            (0.8, -0.2, 1),
            (0.8, 0.2, 1),
            (0.4, 0.2, 1),  # Front
            (0.4, -0.2, -1),
            (0.8, -0.2, -1),
            (0.8, 0.2, -1),
            (0.4, 0.2, -1),  # Rear
            # Connecting Strut
            (-0.4, 0, 0),
            (0.4, 0, 0),
        ]

        edges = [
            # Left Hull
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),  # Front face
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),  # Rear face
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),  # Connecting
            # Right Hull
            (8, 9),
            (9, 10),
            (10, 11),
            (11, 8),  # Front face
            (12, 13),
            (13, 14),
            (14, 15),
            (15, 12),  # Rear face
            (8, 12),
            (9, 13),
            (10, 14),
            (11, 15),  # Connecting
            # Strut
            (16, 17),
            # Connect strut to hulls
            (16, 1),
            (16, 2),
            (16, 5),
            (16, 6),
            (17, 8),
            (17, 11),
            (17, 12),
            (17, 15),
        ]

        return WireframeModel(vertices, edges)

    @staticmethod
    def get_random_builder():
        """Get a random enemy model builder function"""
        import random

        builders = [
            EnemyModelFactory.create_standard,
            EnemyModelFactory.create_scout,
            EnemyModelFactory.create_heavy,
            EnemyModelFactory.create_interceptor,
            EnemyModelFactory.create_bomber,
            EnemyModelFactory.create_frigate,
            EnemyModelFactory.create_stealth,
            EnemyModelFactory.create_assault,
        ]
        return random.choice(builders)


def create_meteorite(size=1.0):
    """Create irregular meteorite wireframe"""
    import random

    # Create simplified irregular asteroid (Deformed Octahedron -ish)
    # Less vertices, more "rocky"

    vertices = []

    # Scale ranges for randomness
    min_s = size * 0.7
    max_s = size * 1.3

    def r_val():
        return random.uniform(min_s, max_s)

    # 6 Base Points (Top, Bottom, Front, Back, Left, Right)
    # But slightly randomized
    v_top = (0, 0, r_val())
    v_bottom = (0, 0, -r_val())

    v_front = (0, r_val(), 0)
    v_back = (0, -r_val(), 0)
    v_right = (r_val(), 0, 0)
    v_left = (-r_val(), 0, 0)

    vertices = [v_top, v_bottom, v_front, v_back, v_right, v_left]

    # Connect them (Octahedron edges)
    edges = [
        # Top pyramid
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        # Bottom pyramid
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        # Equator
        (2, 4),
        (4, 3),
        (3, 5),
        (5, 2),
    ]

    # Optional: Add a few random extra points on faces to break symmetry?
    # For now, base octahedron with uneven axis lengths is a good start for "simple"

    return WireframeModel(vertices, edges)


def create_life_sphere(size=1.0):
    """Create life sphere wireframe"""
    vertices = []
    # Create sphere using latitude/longitude lines
    lat_segments = 8
    lon_segments = 8

    for i in range(lat_segments + 1):
        lat = np.pi * i / lat_segments - np.pi / 2
        for j in range(lon_segments):
            lon = 2 * np.pi * j / lon_segments
            x = size * np.cos(lat) * np.cos(lon)
            y = size * np.cos(lat) * np.sin(lon)
            z = size * np.sin(lat)
            vertices.append((x, y, z))

    edges = []
    # Latitude circles
    for i in range(lat_segments + 1):
        for j in range(lon_segments):
            current = i * lon_segments + j
            next_lon = i * lon_segments + (j + 1) % lon_segments
            edges.append((current, next_lon))

    # Longitude lines
    for i in range(lat_segments):
        for j in range(lon_segments):
            current = i * lon_segments + j
            next_lat = (i + 1) * lon_segments + j
            edges.append((current, next_lat))

    # Add internal cross
    center_idx = len(vertices)
    vertices.append((0, 0, 0))
    # Connect center to poles
    edges.append((center_idx, 0))
    edges.append((center_idx, lon_segments * lat_segments))

    return WireframeModel(vertices, edges)


def create_laser(length=2.0):
    """Create laser projectile wireframe"""
    vertices = [
        # Front tip
        (0, 0, length / 2),
        # Mid ring
        (0.1, 0, 0),
        (-0.1, 0, 0),
        (0, 0.1, 0),
        (0, -0.1, 0),
        # Back
        (0, 0, -length / 2),
    ]

    edges = [
        # Front to mid
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        # Mid ring
        (1, 3),
        (3, 2),
        (2, 4),
        (4, 1),
        # Mid to back
        (1, 5),
        (2, 5),
        (3, 5),
        (4, 5),
    ]

    return WireframeModel(vertices, edges)


def create_cube(size=1.0):
    """Create simple cube for testing"""
    s = size / 2
    vertices = [
        (-s, -s, -s),
        (s, -s, -s),
        (s, s, -s),
        (-s, s, -s),
        (-s, -s, s),
        (s, -s, s),
        (s, s, s),
        (-s, s, s),
    ]

    edges = [
        # Front face
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        # Back face
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        # Connecting edges
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7),
    ]

    return WireframeModel(vertices, edges)
