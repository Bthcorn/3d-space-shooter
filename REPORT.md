# Mini Game 2 — Technical Report

## 1. Material System

The material system is implemented in `engine/materials.py` as a dictionary-based
approach. Each material is a Python dictionary with the keys: `ambient`, `diffuse`,
`specular`, `shininess`, `alpha`, and optionally `emission`.

The `apply_material(mat)` function pushes these values to the OpenGL state using
`glMaterialfv()` and `glMaterialf()` on `GL_FRONT_AND_BACK`. Alpha is injected into
the ambient and diffuse components so that blending works correctly for transparent
materials without needing a separate code path.

Five material categories are defined:

| Material        | Type             | Shininess | Specular | Alpha |
|-----------------|------------------|-----------|----------|-------|
| Matte Gray      | Opaque matte     | 5         | 0.10     | 1.0   |
| Glossy Red      | Opaque glossy    | 70        | 0.90     | 1.0   |
| Metal Silver    | Opaque metallic  | 90        | 0.77     | 1.0   |
| Life Sphere     | Transparent glow | 96        | 0.80     | 0.55  |
| Laser Green/Red | Emissive         | 50        | 0.30     | 0.85  |

Materials are assigned to entities at construction time via the `material` attribute
on the `Entity` base class, making it trivial to change an object's appearance.

## 2. Transparency Approach

Transparency is handled with a deferred rendering strategy:

1. **Opaque pass**: All objects with `alpha == 1.0` are rendered normally with full
   depth testing and depth writing.

2. **Transparent queue**: When `render_solid()` detects `alpha < 1.0`, it appends the
   draw call to an internal `_transparent_queue` list instead of rendering immediately.

3. **Transparent pass** (`render_transparent_objects()`):
   - Objects are sorted **back-to-front** by squared distance to the camera.
   - `glEnable(GL_BLEND)` with `GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA`.
   - `glDepthMask(GL_FALSE)` disables depth writing (but depth *testing* remains on,
     so transparent objects are still occluded by closer opaque geometry).
   - Back-face culling is disabled so both sides of transparent surfaces are visible.
   - After rendering, all state is restored: depth mask re-enabled, blending disabled,
     culling re-enabled.

This approach prevents the common artifact where transparent objects incorrectly occlude
geometry behind them while still participating in depth testing.

## 3. Day/Night Cycle Model

The cycle is driven by a single time parameter `self.time` in `[0, 1)` that advances
each frame by `DAY_NIGHT_CYCLE_SPEED * dt`. A cosine function maps this to a
smooth parameter `t` in `[0, 1]`:

```
t = (1 − cos(2π × time)) / 2
```

This produces a smooth S-curve: `time=0` → midnight (`t=0`),
`time=0.5` → noon (`t=1`), with natural sunrise/sunset transitions and zero
first-derivative at both endpoints (no abrupt switch).

Three visual parameters are driven by `t` (all in `lighting.py`, `apply()` method):

1. **Sky color** (`glClearColor`): Lerps between `SKY_NIGHT` (near-black void) and
   `SKY_DAY` (very dark navy). Both endpoints are dark — space has no atmosphere, so
   the sky is always essentially black. The cycle is visible through the accompanying
   light changes rather than a bright sky colour.

2. **Main light** (`GL_LIGHT0`): Ambient, diffuse, and specular components lerp
   between moon values (faint, cool blue) and sun values (bright, near-neutral white).
   The same light source is used for both roles — there is no GL_LIGHT2. The light
   position orbits using `sin(angle)` for the Y component (no `abs()`), so it crosses
   below the horizon at night; the directional contribution fades naturally as a result.

3. **Global ambient** (`GL_LIGHT_MODEL_AMBIENT`): Lerps between a near-black night fill
   (`0.02, 0.02, 0.05`) and a dim cool noon fill (`0.10, 0.10, 0.14`). Values are
   intentionally low: in space there is no atmospheric scattering, so unlit faces
   should remain nearly black even at noon. The cycle is still clearly perceptible —
   noon is approximately 5× brighter than midnight.

### Starfield

A procedural starfield of 600 points is generated once at startup on a unit sphere
(fixed random seed). Each frame the stars are placed on a sphere of radius
`0.85 × FAR_PLANE` centred on the camera, rendered with depth-write disabled so they
always appear in the background. Star brightness is modulated by `0.55 + 0.45×(1−t)`,
making stars slightly dimmer at noon and brighter at night, reinforcing the cycle.

## 4. Key Design Decisions

**Solid geometry instead of wireframe**: The original Mini Project 1 used `GL_LINES`
exclusively. Since OpenGL fixed-pipeline lighting requires surfaces with normals to
produce shading, all game objects were rebuilt as `SolidModel` instances with
triangulated faces and auto-computed per-face normals. The wireframe models are retained
in the codebase for backward compatibility but are not used in the main render path.

**Per-face normals vs per-vertex normals**: For simplicity and correctness with the
low-poly aesthetic, per-face (flat) normals are used within `GL_SMOOTH` shading mode.
This gives a faceted look that suits the geometric art style while still producing
visible specular highlights.

**Space-correct ambient values**: Terrestrial renderers typically use a warm, moderately
bright ambient to simulate skylight scatter. In a space environment this produces an
unrealistic plain-colour wash. All ambient endpoints are kept below `0.10` so the
directional light (specular + diffuse) does the visual heavy lifting, giving crisp lit
faces and near-black shadows — consistent with ISS photography and space film reference.

**HUD state isolation**: The HUD uses `glPushAttrib(GL_ALL_ATTRIB_BITS)` before any
2D rendering and `glPopAttrib()` afterward, ensuring that disabling lighting/depth for
text rendering does not corrupt the 3D scene state on subsequent frames.
