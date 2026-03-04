"""Main game module — Mini Game 2.

Integrates: lighting, materials, transparency, day/night cycle,
night-vision, enhanced HUD.
"""

import pygame
from pygame.locals import (
    QUIT,
    KEYDOWN,
    KEYUP,
    MOUSEMOTION,
    VIDEORESIZE,
    K_ESCAPE,
    K_r,
    K_SPACE,
    K_w,
    K_s,
    K_a,
    K_d,
    K_n,
    K_t,
    DOUBLEBUF,
    OPENGL,
    RESIZABLE,
)
import random

from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS,
    PLAYER_SPEED, PLAYER_STRAFE_SPEED, PLAYER_MOUSE_SENSITIVITY,
    METEORITE_COUNT, WORLD_SIZE,
    ENEMY_SPAWN_DISTANCE, ENEMY_SPAWN_INTERVAL,
    LIFE_SPHERE_SPAWN_DISTANCE, LIFE_SPHERE_SPAWN_INTERVAL,
    METEORITE_COLLISION_PENALTY, COLLISION_PUSH_BACK,
    SHIP_ROLL_SENSITIVITY, SHIP_PITCH_SENSITIVITY,
    SHIP_ANIMATION_DAMPING, MAX_SHIP_ROLL, MAX_SHIP_PITCH_OFFSET,
)
from game.engine.renderer import Renderer
from game.engine.camera import Camera
from game.engine.physics import CollisionSystem
from game.engine.lighting import LightingSystem
from game.engine.materials import MATERIAL_MATTE_GREEN
from game.entities.player import Player
from game.entities.enemy import Enemy
from game.entities.meteorite import Meteorite
from game.entities.life_sphere import LifeSphere
from game.entities.explosion import Explosion
from game.entities.projectile import Projectile
from game.ui.hud import HUD
from game.utils.math_utils import Vector3


class Game:
    """Main game class — Mini Game 2."""

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL | RESIZABLE
        )
        pygame.display.set_caption(WINDOW_TITLE)

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        # Core systems
        self.renderer = Renderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.hud = HUD(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.camera = Camera(Vector3(0, 0, 5))
        self.collision_system = CollisionSystem()
        self.lighting = LightingSystem()

        # Ship animation tracking
        self.previous_camera_yaw = self.camera.yaw
        self.previous_camera_pitch = self.camera.pitch
        self.ship_roll = 0.0
        self.ship_pitch_offset = 0.0
        self.ship_yaw_offset = 0.0

        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.game_over = False
        self.score = 0

        # Entities
        self.player = Player(Vector3(0, 0, 0))
        self.enemies = []
        self.meteorites = []
        self.life_spheres = []
        self.projectiles = []
        self.explosions = []

        # Radar / detection mode
        self.radar_active = False  # Toggle with T key

        # Spawn timers
        self.enemy_spawn_timer = 0.0
        self.life_sphere_spawn_timer = 0.0

        # Movement state
        self.keys_pressed = set()
        self.cockpit_sway = 0.0

        # Init world
        self._spawn_initial_meteorites()

    # ------------------------------------------------------------------
    # Spawning
    # ------------------------------------------------------------------

    def _spawn_initial_meteorites(self):
        for _ in range(METEORITE_COUNT):
            pos = Vector3(
                random.uniform(-WORLD_SIZE / 2, WORLD_SIZE / 2),
                random.uniform(-WORLD_SIZE / 4, WORLD_SIZE / 4),
                random.uniform(-WORLD_SIZE, -20),
            )
            self.meteorites.append(Meteorite(pos))

    def _spawn_enemy(self):
        distance = ENEMY_SPAWN_DISTANCE
        pos = Vector3(
            self.camera.position.x + distance * random.uniform(-0.5, 0.5),
            self.camera.position.y + random.uniform(-10, 10),
            self.camera.position.z - distance,
        )
        from game.utils.models import EnemyModelFactory
        model_factory = EnemyModelFactory.get_random_builder()
        self.enemies.append(Enemy(pos, model_factory))

    def _spawn_life_sphere(self):
        pos = Vector3(
            self.camera.position.x + random.uniform(-30, 30),
            self.camera.position.y + random.uniform(-20, 20),
            self.camera.position.z - random.uniform(30, LIFE_SPHERE_SPAWN_DISTANCE),
        )
        self.life_spheres.append(LifeSphere(pos))

    def _shoot_player_laser(self):
        if self.player.shoot():
            direction = self.camera.get_forward_vector()
            pos = self.camera.position + direction * 2
            self.projectiles.append(Projectile(pos, direction, "player"))

    def _shoot_enemy_laser(self, enemy):
        direction = enemy.get_shoot_direction(self.player.position)
        pos = enemy.position.copy()
        self.projectiles.append(Projectile(pos, direction, "enemy"))

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.game_over:
                        self.running = False
                    else:
                        self.paused = not self.paused

                elif event.key == K_r and self.game_over:
                    self._restart_game()

                elif event.key == K_SPACE and not self.paused and not self.game_over:
                    self._shoot_player_laser()

                # --- Mini Game 2: new interactions ---
                elif event.key == K_n and not self.paused:
                    self.lighting.toggle_night_vision()

                elif event.key == K_t and not self.paused:
                    self.radar_active = not self.radar_active

                self.keys_pressed.add(event.key)

            elif event.type == KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.remove(event.key)

            elif event.type == MOUSEMOTION and not self.paused and not self.game_over:
                dx, dy = event.rel
                self.camera.process_mouse_movement(
                    dx * PLAYER_MOUSE_SENSITIVITY,
                    -dy * PLAYER_MOUSE_SENSITIVITY,
                )

            elif event.type == VIDEORESIZE:
                self.renderer.resize(event.w, event.h)
                self.hud.resize(event.w, event.h)

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def handle_movement(self, dt):
        if self.paused or self.game_over:
            return

        if K_w in self.keys_pressed:
            self.camera.move_forward(PLAYER_SPEED * dt)
        if K_s in self.keys_pressed:
            self.camera.move_backward(PLAYER_SPEED * dt)
        if K_a in self.keys_pressed:
            self.camera.move_left(PLAYER_STRAFE_SPEED * dt)
        if K_d in self.keys_pressed:
            self.camera.move_right(PLAYER_STRAFE_SPEED * dt)

        self.player.position = self.camera.position.copy()

    # ------------------------------------------------------------------
    # Ship animation
    # ------------------------------------------------------------------

    def _update_ship_animation(self, dt):
        yaw_delta = self.camera.yaw - self.previous_camera_yaw
        pitch_delta = self.camera.pitch - self.previous_camera_pitch

        while yaw_delta > 180:
            yaw_delta -= 360
        while yaw_delta < -180:
            yaw_delta += 360

        yaw_delta = max(-10, min(10, yaw_delta))
        pitch_delta = max(-10, min(10, pitch_delta))

        target_roll = -yaw_delta * SHIP_ROLL_SENSITIVITY
        target_roll = max(-MAX_SHIP_ROLL, min(MAX_SHIP_ROLL, target_roll))

        damping = min(1.0, SHIP_ANIMATION_DAMPING * dt)
        self.ship_roll += (target_roll - self.ship_roll) * damping
        self.ship_roll = max(-MAX_SHIP_ROLL, min(MAX_SHIP_ROLL, self.ship_roll))

        target_pitch = pitch_delta * SHIP_PITCH_SENSITIVITY
        target_pitch = max(-MAX_SHIP_PITCH_OFFSET, min(MAX_SHIP_PITCH_OFFSET, target_pitch))
        self.ship_pitch_offset += (target_pitch - self.ship_pitch_offset) * damping
        self.ship_pitch_offset = max(-MAX_SHIP_PITCH_OFFSET, min(MAX_SHIP_PITCH_OFFSET, self.ship_pitch_offset))

        if abs(yaw_delta) < 0.5:
            self.ship_roll *= 0.92
        if abs(pitch_delta) < 0.5:
            self.ship_pitch_offset *= 0.92
        if abs(self.ship_roll) < 0.1:
            self.ship_roll = 0.0
        if abs(self.ship_pitch_offset) < 0.1:
            self.ship_pitch_offset = 0.0

        self.previous_camera_yaw = self.camera.yaw
        self.previous_camera_pitch = self.camera.pitch

        # Cockpit sway
        target_sway = 0.0
        if K_a in self.keys_pressed:
            target_sway = -40.0
        elif K_d in self.keys_pressed:
            target_sway = 40.0
        self.cockpit_sway += (target_sway - self.cockpit_sway) * 5.0 * dt

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt):
        if self.paused or self.game_over:
            return

        # Day/night cycle
        self.lighting.update(dt)

        self._update_ship_animation(dt)
        self.player.update(dt)

        for enemy in self.enemies[:]:
            enemy.update(dt, self.player.position)
            if enemy.can_shoot(self.player.position):
                self._shoot_enemy_laser(enemy)

        for meteorite in self.meteorites:
            meteorite.update(dt)

        for sphere in self.life_spheres:
            sphere.update(dt)

        for projectile in self.projectiles:
            projectile.update(dt)

        for explosion in self.explosions:
            explosion.update(dt)

        self._update_spawning(dt)
        self._handle_collisions()
        self._cleanup_entities()

    def _update_spawning(self, dt):
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self.enemy_spawn_timer = 0
            self._spawn_enemy()

        self.life_sphere_spawn_timer += dt
        if self.life_sphere_spawn_timer >= LIFE_SPHERE_SPAWN_INTERVAL:
            self.life_sphere_spawn_timer = 0
            self._spawn_life_sphere()

    def _handle_collisions(self):
        # Player vs Meteorites
        for meteorite in self.meteorites:
            if self.collision_system.check_collision(self.player, meteorite):
                self.score += METEORITE_COLLISION_PENALTY
                self.collision_system.resolve_collision(
                    self.player, meteorite, COLLISION_PUSH_BACK
                )
                self.camera.position = self.player.position.copy()

        # Player vs Life Spheres
        for sphere in self.life_spheres[:]:
            if self.collision_system.check_collision(self.player, sphere):
                self.player.add_life()
                sphere.collect()

        # Player vs Enemy
        for enemy in self.enemies[:]:
            if self.collision_system.check_collision(self.player, enemy):
                self.player.take_damage()
                enemy.destroy()
                self.explosions.append(Explosion(enemy.position.copy()))

        # Projectiles
        for projectile in self.projectiles[:]:
            if projectile.is_player_projectile():
                for enemy in self.enemies[:]:
                    if self.collision_system.check_collision(projectile, enemy):
                        enemy.take_damage()
                        projectile.destroy()
                        if not enemy.is_alive():
                            self.score += enemy.get_points()
                            self.explosions.append(Explosion(enemy.position.copy()))
                        break
                for sphere in self.life_spheres[:]:
                    if self.collision_system.check_collision(projectile, sphere):
                        self.player.add_life()
                        sphere.collect()
                        projectile.destroy()
                        break
                for meteorite in self.meteorites:
                    if self.collision_system.check_collision(projectile, meteorite):
                        projectile.destroy()
                        break
            elif projectile.is_enemy_projectile():
                if self.collision_system.check_collision(projectile, self.player):
                    self.player.take_damage()
                    projectile.destroy()
                for meteorite in self.meteorites:
                    if self.collision_system.check_collision(projectile, meteorite):
                        projectile.destroy()
                        break

        if not self.player.is_alive():
            self.game_over = True

    def _cleanup_entities(self):
        self.enemies = [e for e in self.enemies if e.is_alive()]
        self.life_spheres = [s for s in self.life_spheres if s.is_alive()]
        self.projectiles = [p for p in self.projectiles if p.is_alive()]
        self.explosions = [e for e in self.explosions if e.is_alive()]

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self):
        self.renderer.begin_frame()
        self.renderer.apply_camera(self.camera)

        # Apply lighting (must be AFTER camera/modelview is set)
        self.lighting.apply(camera=self.camera)

        # --- 0. Starfield (always-background, depth-write off) ---
        self.renderer.render_starfield(
            self.camera.position,
            day_factor=self.lighting.get_day_factor(),
        )

        # --- 1. Opaque objects first ---

        # Ground plane (matte green)
        self.renderer.render_ground_plane(
            MATERIAL_MATTE_GREEN, self.camera.position,
            size=400, spacing=10,
        )

        # Enemies (glossy red — opaque)
        for enemy in self.enemies:
            if enemy.solid_model:
                self.renderer.render_solid(
                    enemy.solid_model, enemy.position,
                    enemy.rotation, enemy.scale, enemy.material,
                )

        # Meteorites (matte gray — opaque)
        for meteorite in self.meteorites:
            if meteorite.solid_model:
                self.renderer.render_solid(
                    meteorite.solid_model, meteorite.position,
                    meteorite.rotation, meteorite.scale, meteorite.material,
                )

        # Explosions (emissive, semi-transparent)
        for explosion in self.explosions:
            if explosion.solid_model:
                self.renderer.render_solid(
                    explosion.solid_model,
                    explosion.position,
                    explosion.rotation,
                    explosion.scale,
                    explosion.material,
                )

        # Projectiles (emissive — semi-transparent, queued automatically)
        for projectile in self.projectiles:
            if projectile.solid_model:
                self.renderer.render_solid(
                    projectile.solid_model, projectile.position,
                    projectile.rotation, projectile.scale, projectile.material,
                )

        # Life spheres (transparent — queued automatically)
        for sphere in self.life_spheres:
            if sphere.solid_model:
                self.renderer.render_solid(
                    sphere.solid_model, sphere.position,
                    sphere.rotation, sphere.scale, sphere.material,
                )

        # --- 2. Transparent pass (sorted, depth-write disabled) ---
        self.renderer.render_transparent_objects(camera_pos=self.camera.position)

        # --- 3. HUD overlay (disables lighting internally) ---
        fps = int(self.clock.get_fps())
        cooldown_ratio = 0.0
        if self.player.shoot_cooldown > 0:
            from game.config import PLAYER_SHOOT_COOLDOWN
            cooldown_ratio = self.player.shoot_cooldown / PLAYER_SHOOT_COOLDOWN

        self.hud.render(
            self.player.get_lives(),
            self.score,
            cooldown_ratio,
            self.ship_roll,
            self.player.damage_flash_timer,
            self.player.position,
            self.camera.yaw,
            self.cockpit_sway,
            fps,
            day_factor=self.lighting.get_day_factor(),
            time_label=self.lighting.get_time_of_day_string(),
            night_vision=self.lighting.night_vision,
            radar_active=self.radar_active,
            enemies=self.enemies,
            camera=self.camera,
        )

        if self.game_over:
            self.hud.render_game_over(self.score)
        elif self.paused:
            self.hud.render_pause()

        self.renderer.end_frame()

    # ------------------------------------------------------------------
    # Restart
    # ------------------------------------------------------------------

    def _restart_game(self):
        self.game_over = False
        self.paused = False
        self.score = 0

        self.player = Player(Vector3(0, 0, 0))
        self.camera = Camera(Vector3(0, 0, 5))

        self.previous_camera_yaw = self.camera.yaw
        self.previous_camera_pitch = self.camera.pitch
        self.ship_roll = 0.0
        self.ship_pitch_offset = 0.0
        self.ship_yaw_offset = 0.0

        self.enemies.clear()
        self.meteorites.clear()
        self.life_spheres.clear()
        self.projectiles.clear()

        self.enemy_spawn_timer = 0.0
        self.life_sphere_spawn_timer = 0.0
        self.radar_active = False

        self._spawn_initial_meteorites()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.handle_movement(dt)
            self.update(dt)
            self.render()

        pygame.quit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
