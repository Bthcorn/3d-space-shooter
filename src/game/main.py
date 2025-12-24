"""Main game module - handles game loop and logic"""

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
    DOUBLEBUF,
    OPENGL,
    RESIZABLE,
)
import random

from game.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    FPS,
    PLAYER_SPEED,
    PLAYER_STRAFE_SPEED,
    PLAYER_MOUSE_SENSITIVITY,
    METEORITE_COUNT,
    WORLD_SIZE,
    ENEMY_SPAWN_DISTANCE,
    ENEMY_SPAWN_INTERVAL,
    LIFE_SPHERE_SPAWN_DISTANCE,
    LIFE_SPHERE_SPAWN_INTERVAL,
    METEORITE_COLLISION_PENALTY,
    COLLISION_PUSH_BACK,
)
from game.engine.renderer import Renderer
from game.engine.camera import Camera
from game.engine.physics import CollisionSystem
from game.entities.player import Player
from game.entities.enemy import Enemy
from game.entities.meteorite import Meteorite
from game.entities.life_sphere import LifeSphere
from game.entities.projectile import Projectile
from game.ui.hud import HUD
from game.utils.math_utils import Vector3


class Game:
    """Main game class"""

    def __init__(self):
        """Initialize game"""
        pygame.init()

        # Create window
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL | RESIZABLE
        )
        pygame.display.set_caption(WINDOW_TITLE)

        # Hide and capture mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        # Initialize systems
        self.renderer = Renderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.hud = HUD(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.camera = Camera(Vector3(0, 0, 5))
        self.collision_system = CollisionSystem()

        # Track camera movement for ship animation
        self.previous_camera_yaw = self.camera.yaw
        self.previous_camera_pitch = self.camera.pitch
        self.ship_roll = 0.0  # Ship banking/rolling
        self.ship_pitch_offset = 0.0  # Additional pitch from movement
        self.ship_yaw_offset = 0.0  # Additional yaw from movement

        # Game state
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.game_over = False
        self.score = 0

        # Entity lists
        self.player = Player(Vector3(0, 0, 0))
        self.enemies = []
        self.meteorites = []
        self.life_spheres = []
        self.projectiles = []

        # Spawn timers
        self.enemy_spawn_timer = 0.0
        self.life_sphere_spawn_timer = 0.0

        # Initialize world
        self._spawn_initial_meteorites()

        # Movement state
        self.keys_pressed = set()
        self.cockpit_sway = 0.0

    def _spawn_initial_meteorites(self):
        """Spawn initial meteorites around the world"""
        for _ in range(METEORITE_COUNT):
            pos = Vector3(
                random.uniform(-WORLD_SIZE / 2, WORLD_SIZE / 2),
                random.uniform(-WORLD_SIZE / 4, WORLD_SIZE / 4),
                random.uniform(-WORLD_SIZE, -20),
            )
            self.meteorites.append(Meteorite(pos))

    def _spawn_enemy(self):
        """Spawn a new enemy"""
        # Spawn enemy in front of player
        angle = random.uniform(0, 6.28)  # Random angle
        distance = ENEMY_SPAWN_DISTANCE

        pos = Vector3(
            self.camera.position.x + distance * random.uniform(-0.5, 0.5),
            self.camera.position.y + random.uniform(-10, 10),
            self.camera.position.z - distance,
        )

        # Randomly select enemy model
        # Randomly select enemy model
        from game.utils.models import EnemyModelFactory

        model_factory = EnemyModelFactory.get_random_builder()

        self.enemies.append(Enemy(pos, model_factory))

    def _spawn_life_sphere(self):
        """Spawn a new life sphere"""
        pos = Vector3(
            self.camera.position.x + random.uniform(-30, 30),
            self.camera.position.y + random.uniform(-20, 20),
            self.camera.position.z - random.uniform(30, LIFE_SPHERE_SPAWN_DISTANCE),
        )

        self.life_spheres.append(LifeSphere(pos))

    def _shoot_player_laser(self):
        """Player shoots a laser"""
        if self.player.shoot():
            direction = self.camera.get_forward_vector()
            pos = self.camera.position + direction * 2  # Spawn in front of camera
            self.projectiles.append(Projectile(pos, direction, "player"))

    def _shoot_enemy_laser(self, enemy):
        """Enemy shoots a laser"""
        direction = enemy.get_shoot_direction(self.player.position)
        pos = enemy.position.copy()
        self.projectiles.append(Projectile(pos, direction, "enemy"))

    def handle_events(self):
        """Handle input events"""
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

                self.keys_pressed.add(event.key)

            elif event.type == KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.remove(event.key)

            elif event.type == MOUSEMOTION and not self.paused and not self.game_over:
                dx, dy = event.rel
                self.camera.process_mouse_movement(
                    dx * PLAYER_MOUSE_SENSITIVITY, -dy * PLAYER_MOUSE_SENSITIVITY
                )

            elif event.type == VIDEORESIZE:
                self.renderer.resize(event.w, event.h)
                self.hud.resize(event.w, event.h)

    def handle_movement(self, dt):
        """Handle continuous movement"""
        if self.paused or self.game_over:
            return

        # Camera/Player movement
        if K_w in self.keys_pressed:
            self.camera.move_forward(PLAYER_SPEED * dt)
        if K_s in self.keys_pressed:
            self.camera.move_backward(PLAYER_SPEED * dt)
        if K_a in self.keys_pressed:
            self.camera.move_left(PLAYER_STRAFE_SPEED * dt)
        if K_d in self.keys_pressed:
            self.camera.move_right(PLAYER_STRAFE_SPEED * dt)

        # Update player position to match camera
        self.player.position = self.camera.position.copy()

    def _update_ship_animation(self, dt):
        """
        Update ship rotation/tilt based on camera movement
        Creates dynamic banking and pitching effects
        """
        from game.config import (
            SHIP_ROLL_SENSITIVITY,
            SHIP_PITCH_SENSITIVITY,
            SHIP_ANIMATION_DAMPING,
            MAX_SHIP_ROLL,
            MAX_SHIP_PITCH_OFFSET,
        )

        # Calculate camera rotation changes
        yaw_delta = self.camera.yaw - self.previous_camera_yaw
        pitch_delta = self.camera.pitch - self.previous_camera_pitch

        # Normalize yaw delta (handle wraparound at 360/-180 degrees)
        while yaw_delta > 180:
            yaw_delta -= 360
        while yaw_delta < -180:
            yaw_delta += 360

        # Clamp deltas to prevent extreme values
        yaw_delta = max(-10, min(10, yaw_delta))
        pitch_delta = max(-10, min(10, pitch_delta))

        # Banking/rolling when turning left/right (yaw)
        # Negative because turning left should bank left (negative roll)
        target_roll = -yaw_delta * SHIP_ROLL_SENSITIVITY

        # Clamp target roll immediately
        target_roll = max(-MAX_SHIP_ROLL, min(MAX_SHIP_ROLL, target_roll))

        # Smooth roll transition with damping
        damping_factor = min(1.0, SHIP_ANIMATION_DAMPING * dt)
        self.ship_roll += (target_roll - self.ship_roll) * damping_factor

        # Additional clamping to be safe
        self.ship_roll = max(-MAX_SHIP_ROLL, min(MAX_SHIP_ROLL, self.ship_roll))

        # Pitch offset when looking up/down
        target_pitch_offset = pitch_delta * SHIP_PITCH_SENSITIVITY

        # Clamp target pitch
        target_pitch_offset = max(
            -MAX_SHIP_PITCH_OFFSET, min(MAX_SHIP_PITCH_OFFSET, target_pitch_offset)
        )

        # Smooth pitch transition
        self.ship_pitch_offset += (target_pitch_offset - self.ship_pitch_offset) * damping_factor

        # Additional clamping
        self.ship_pitch_offset = max(
            -MAX_SHIP_PITCH_OFFSET, min(MAX_SHIP_PITCH_OFFSET, self.ship_pitch_offset)
        )

        # Damping - gradually return to neutral when not moving camera
        if abs(yaw_delta) < 0.5:
            self.ship_roll *= 0.92  # Decay towards zero
        if abs(pitch_delta) < 0.5:
            self.ship_pitch_offset *= 0.92  # Decay towards zero

        # Safety: Force to zero if very small
        if abs(self.ship_roll) < 0.1:
            self.ship_roll = 0.0
        if abs(self.ship_pitch_offset) < 0.1:
            self.ship_pitch_offset = 0.0

        # Update previous camera state
        self.previous_camera_yaw = self.camera.yaw
        self.previous_camera_pitch = self.camera.pitch

        # --- Cockpit Inertia (Sway) ---
        target_sway = 0.0
        keys = pygame.key.get_pressed()

        # Turn Left (A) -> HUD Frame Shift Left (relative to screen center) to simulate head lag Right
        if keys[K_a]:
            target_sway = -40.0
        elif keys[K_d]:
            target_sway = 40.0

        # Smooth sway transition
        sway_speed = 5.0 * dt
        self.cockpit_sway += (target_sway - self.cockpit_sway) * sway_speed

    def update(self, dt):
        """Update game state"""
        if self.paused or self.game_over:
            return

        # Update ship animation based on camera movement
        self._update_ship_animation(dt)

        # Update player
        self.player.update(dt)

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, self.player.position)

            # Enemy AI shooting
            if enemy.can_shoot(self.player.position):
                self._shoot_enemy_laser(enemy)

        # Update meteorites
        for meteorite in self.meteorites:
            meteorite.update(dt)

        # Update life spheres
        for sphere in self.life_spheres:
            sphere.update(dt)

        # Update projectiles
        for projectile in self.projectiles:
            projectile.update(dt)

        # Spawning
        self._update_spawning(dt)

        # Collision detection
        self._handle_collisions()

        # Remove dead entities
        self._cleanup_entities()

    def _update_spawning(self, dt):
        """Update enemy and power-up spawning"""
        # Spawn enemies
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self.enemy_spawn_timer = 0
            self._spawn_enemy()

        # Spawn life spheres
        self.life_sphere_spawn_timer += dt
        if self.life_sphere_spawn_timer >= LIFE_SPHERE_SPAWN_INTERVAL:
            self.life_sphere_spawn_timer = 0
            self._spawn_life_sphere()

    def _handle_collisions(self):
        """Handle all collision detection"""
        # Player vs Meteorites
        for meteorite in self.meteorites:
            if self.collision_system.check_collision(self.player, meteorite):
                self.score += METEORITE_COLLISION_PENALTY
                # Push player back
                self.collision_system.resolve_collision(self.player, meteorite, COLLISION_PUSH_BACK)
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

        # Projectiles
        for projectile in self.projectiles[:]:
            # Player projectiles vs enemies
            if projectile.is_player_projectile():
                for enemy in self.enemies[:]:
                    if self.collision_system.check_collision(projectile, enemy):
                        enemy.take_damage()
                        projectile.destroy()
                        if not enemy.is_alive():
                            self.score += enemy.get_points()
                        break

                # Player projectiles vs life spheres
                for sphere in self.life_spheres[:]:
                    if self.collision_system.check_collision(projectile, sphere):
                        self.player.add_life()
                        sphere.collect()
                        projectile.destroy()
                        break

                # Player projectiles vs meteorites (block)
                for meteorite in self.meteorites:
                    if self.collision_system.check_collision(projectile, meteorite):
                        projectile.destroy()
                        break

            # Enemy projectiles vs player
            elif projectile.is_enemy_projectile():
                if self.collision_system.check_collision(projectile, self.player):
                    self.player.take_damage()
                    projectile.destroy()

                # Enemy projectiles vs meteorites (block)
                for meteorite in self.meteorites:
                    if self.collision_system.check_collision(projectile, meteorite):
                        projectile.destroy()
                        break

        # Check if player is dead
        if not self.player.is_alive():
            self.game_over = True

    def _cleanup_entities(self):
        """Remove dead entities"""
        self.enemies = [e for e in self.enemies if e.is_alive()]
        self.life_spheres = [s for s in self.life_spheres if s.is_alive()]
        self.projectiles = [p for p in self.projectiles if p.is_alive()]

    def render(self):
        """Render game"""
        self.renderer.begin_frame()
        self.renderer.apply_camera(self.camera)

        # Render player ship attached to camera (cockpit view)
        # self.renderer.render_player_ship(
        #     self.player, self.camera, self.ship_roll, self.ship_pitch_offset
        # )

        # Render enemies
        for enemy in self.enemies:
            self.renderer.render_wireframe(
                enemy.model,
                enemy.position,
                enemy.rotation,
                enemy.scale,
                enemy.get_color(),
            )

        # Render meteorites
        for meteorite in self.meteorites:
            self.renderer.render_wireframe(
                meteorite.model,
                meteorite.position,
                meteorite.rotation,
                meteorite.scale,
                meteorite.get_color(),
            )

        # Render life spheres
        for sphere in self.life_spheres:
            self.renderer.render_wireframe(
                sphere.model,
                sphere.position,
                sphere.rotation,
                sphere.scale,
                sphere.get_color(),
            )

        # Render projectiles
        for projectile in self.projectiles:
            self.renderer.render_wireframe(
                projectile.model,
                projectile.position,
                projectile.rotation,
                projectile.scale,
                projectile.get_color(),
            )

        # Render crosshair
        # self.renderer.render_crosshair()

        # Render HUD
        fps = int(self.clock.get_fps())

        # Calculate cooldown ratio (0.0 to 1.0)
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
            # self.enemies,
            self.player.position,
            self.camera.yaw,
            self.cockpit_sway,
            fps,
        )

        # Render game over or pause screen
        if self.game_over:
            self.hud.render_game_over(self.score)
        elif self.paused:
            self.hud.render_pause()

        self.renderer.end_frame()

    def _restart_game(self):
        """Restart the game"""
        self.game_over = False
        self.paused = False
        self.score = 0

        # Reset player
        self.player = Player(Vector3(0, 0, 0))
        self.camera = Camera(Vector3(0, 0, 5))

        # Reset ship animation
        self.previous_camera_yaw = self.camera.yaw
        self.previous_camera_pitch = self.camera.pitch
        self.ship_roll = 0.0
        self.ship_pitch_offset = 0.0
        self.ship_yaw_offset = 0.0

        # Clear entities
        self.enemies.clear()
        self.meteorites.clear()
        self.life_spheres.clear()
        self.projectiles.clear()

        # Reset timers
        self.enemy_spawn_timer = 0.0
        self.life_sphere_spawn_timer = 0.0

        # Respawn meteorites
        self._spawn_initial_meteorites()

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            self.handle_events()
            self.handle_movement(dt)
            self.update(dt)
            self.render()

        pygame.quit()


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
