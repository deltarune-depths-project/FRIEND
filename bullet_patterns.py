import math
import random

from arcade.easing import ease_out

import settings
from bullet_board import BulletBoard
from bullets import Bullet, BlackDiamondBullet, CatBullet, TailCircleBullet, TailPointBullet
from math_methods import ease_out_quint
from soul import Soul
from sprites_and_effects_collection import SpritesAndEffectsCollection


class BulletPattern:
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, total_duration: float = 10.0,
                 attacker = None):
        self.sprites_and_effects_collection = sprites_and_effects_collection
        self.total_duration = total_duration
        self.attacker = attacker

        self.time = 0
        self.bullets = [] # When spawning a bullet, add it to this list so it can be cleaned up later
        self.bullet_sprites = []
        self.total_duration = total_duration
        self.is_terminated = False

    def update_animation(self, delta_time: float):
        self.time += delta_time

        if self.time > self.total_duration:
            self.terminate_animation()

    def terminate_animation(self):
        self.is_terminated = True

        for bullet in self.bullets:
            if bullet in self.sprites_and_effects_collection.effects:
                self.sprites_and_effects_collection.effects.remove(bullet)
        for bullet_sprite in self.bullet_sprites:
            bullet_sprite.kill()

    def spawn_bullet(self, bullet: Bullet):
        """
        Add bullets to the bullets sprite list. Also adds the new sprites to the effects sprite list.
        :return: None
        """
        if hasattr(bullet, "get_sprites"):
            for sprite in bullet.get_sprites():
                self.bullet_sprites.append(sprite)
                self.sprites_and_effects_collection.bullet_sprites.append(sprite)
        else:
            self.bullet_sprites.append(bullet)
            self.sprites_and_effects_collection.bullet_sprites.append(bullet)

        self.bullets.append(bullet)
        self.sprites_and_effects_collection.effects.append(bullet)

    def spawn_bullets(self, bullets: list[Bullet]):
        """
        Add sprites to the bullets sprite list. Also adds the new sprites to the effects sprite list.
        :return: None
        """
        for bullet in bullets:
            self.spawn_bullet(bullet)


class RainingDiamondBulletPattern(BulletPattern):
    def __init__(self, sprites_and_effects_collection, bullet_board: BulletBoard, total_duration: float = 20.0,
                 frequency: float = 1.0, attacker = None):
        super().__init__(
            sprites_and_effects_collection=sprites_and_effects_collection,
            total_duration=total_duration,
            attacker=attacker
        )

        self.bullet_board = bullet_board
        self.time_since_last_diamond_spawned = 0.0
        self.diamond_frequency = frequency / 4  # The amount of time in seconds between each diamond spawn

    def update_animation(self, delta_time: float):
        super().update_animation(delta_time)

        self.time_since_last_diamond_spawned += delta_time
        if self.time_since_last_diamond_spawned > self.diamond_frequency:
            bullet = BlackDiamondBullet(
                center_x=random.randint(self.bullet_board.bullet_board_sprite.left, self.bullet_board.bullet_board_sprite.right),
                center_y=self.bullet_board.bullet_board_sprite.top + 20,
                attacker=self.attacker
            )
            self.spawn_bullet(bullet)

            self.time_since_last_diamond_spawned = 0.0


class CatPounceBulletPattern(BulletPattern):
    def __init__(self, sprites_and_effects_collection, soul: Soul, total_duration: float = 10.0, attacker = None):
        super().__init__(
            sprites_and_effects_collection=sprites_and_effects_collection,
            total_duration=total_duration,
            attacker=attacker
        )

        self.soul = soul

        self.number_of_cats = 9
        self.distance_between_each_cat = settings.WINDOW_WIDTH / self.number_of_cats
        self.number_of_frames_per_cat_spawn = self.distance_between_each_cat / 2.5
        self.frames_elapsed_since_last_cat_spawn = 0
        for i in range(self.number_of_cats + 2):
            cat_bullet = CatBullet(
                sprites_and_effects_collection=sprites_and_effects_collection,
                center_x=i*self.distance_between_each_cat,  # random.randint(settings.WINDOW_CENTER_X - 300, settings.WINDOW_CENTER_X + 300),
                center_y=(settings.WINDOW_HEIGHT / 3) + 72,
                attacker=self.attacker,
                soul=self.soul
            )

            self.spawn_bullet(cat_bullet)

    def update_animation(self, delta_time: float):
        super().update_animation(delta_time)
        self.frames_elapsed_since_last_cat_spawn += 1
        # Spawn another cat if the last cat goes off the screen
        if self.frames_elapsed_since_last_cat_spawn >= self.number_of_frames_per_cat_spawn:
            self.frames_elapsed_since_last_cat_spawn = 0
            self.bullets.pop(0)
            cat_bullet = CatBullet(
                sprites_and_effects_collection=self.sprites_and_effects_collection,
                center_x=settings.WINDOW_WIDTH + self.distance_between_each_cat,
                # random.randint(settings.WINDOW_CENTER_X - 300, settings.WINDOW_CENTER_X + 300),
                center_y=(settings.WINDOW_HEIGHT / 3) + 72,
                attacker=self.attacker,
                soul=self.soul
            )
            self.spawn_bullet(cat_bullet)

    def terminate_animation(self):
        super().terminate_animation()
        for bullet in self.sprites_and_effects_collection.bullet_sprites:
            if bullet in self.sprites_and_effects_collection.effects:
                self.sprites_and_effects_collection.effects.remove(bullet)
            bullet.kill()


class PointedTailStabBulletPattern(BulletPattern):
    def __init__(self, sprites_and_effects_collection, soul: Soul = None, total_duration: float = 10.0, attacker = None):
        super().__init__(
            sprites_and_effects_collection=sprites_and_effects_collection,
            total_duration=total_duration,
            attacker=attacker
        )

        self.soul = soul

        self.tail_segments = []

        self.starting_x = int(settings.WINDOW_WIDTH)
        self.starting_y = int(settings.WINDOW_HEIGHT / 2) + 120

        self.number_of_tail_segments = 16
        for i in range(self.number_of_tail_segments):
            tail_circle = TailCircleBullet(
                center_x=self.starting_x,
                center_y=self.starting_y,
                sprites_and_effects_collection=sprites_and_effects_collection,
                attacker=attacker
            )

            self.tail_segments.append(tail_circle)

        self.spawn_bullets(self.tail_segments)

        self.tail_point = TailPointBullet(
            center_x=self.starting_x,
            center_y=self.starting_y,
            angle=90,
            sprites_and_effects_collection=sprites_and_effects_collection,
            attacker=attacker
        )

        self.spawn_bullet(self.tail_point)

        # Animation variables
        self.rotation_duration = 1.0
        self.rotation_radius = 15
        self.wavelength = 0.2
        self.time_elapsed_since_tail_retraction = 0.0

        # The arcade module and the math module have their 0 degree starting points 90 degrees apart
        self.tail_angle = self.tail_point.angle + 90
        self.tail_angle_in_radians = math.radians(self.tail_angle)
        self.sin_of_tail_angle_in_radians = math.sin(math.radians(self.tail_angle))
        self.cos_of_tail_angle_in_radians = math.cos(math.radians(self.tail_angle))

        self.max_length_of_tail = 1200
        self.tail_extension_duration = 0.5
        self.ending_x = self.starting_x + (self.max_length_of_tail * math.cos(self.tail_angle_in_radians))
        self.ending_y = self.starting_y + (self.max_length_of_tail * math.sin(self.tail_angle_in_radians))
        self.tail_point_dx = self.ending_x - self.starting_x
        self.tail_point_dy = self.ending_y - self.starting_y

        self.duration_before_tail_retract = 1.0
        self.distance_between_max_extended_tail_segments = self.max_length_of_tail / self.number_of_tail_segments
        self.t = 1.0

        # Animation flags
        self.tail_not_fully_extended = True
        self.tail_hasnt_started_retracting = True
        self.tail_retract_positions_not_set = True

    def update_animation(self, delta_time: float):
        super().update_animation(delta_time)

        radians = (self.time * math.pi) / self.rotation_duration
        num_of_tail_segments_plus_point = len(self.bullets)

        for i in range(num_of_tail_segments_plus_point):
            current_bullet = self.bullets[i]
            if self.tail_not_fully_extended and self.time < self.tail_extension_duration:
                # Shoot the tail out to the left
                fraction_of_ease = i / num_of_tail_segments_plus_point
                current_bullet.center_x = self.starting_x + (self.tail_point_dx * ease_out_quint((self.time / self.tail_extension_duration)) * fraction_of_ease)
                current_bullet.center_y = self.starting_y + (self.tail_point_dy * ease_out_quint((self.time / self.tail_extension_duration)) * fraction_of_ease)
            else:
                if self.tail_not_fully_extended:
                    fraction_of_ease = i / num_of_tail_segments_plus_point
                    current_bullet.center_x = self.starting_x + (self.tail_point_dx * fraction_of_ease)
                    current_bullet.center_y = self.starting_y + (self.tail_point_dy * fraction_of_ease)
                    self.tail_not_fully_extended = False
                if self.time < self.duration_before_tail_retract:
                    # Bob the tail segments up and down
                    current_bullet.center_y = current_bullet.initial_center_x + (
                            self.rotation_radius * math.cos(radians))
                    current_bullet.center_y = current_bullet.initial_center_y + (
                                self.rotation_radius * math.sin(radians))
                    radians -= ((self.rotation_duration / num_of_tail_segments_plus_point) * (
                                math.pi / 2)) / self.wavelength
                else:
                    if self.tail_hasnt_started_retracting:
                        current_bullet.initial_center_x = current_bullet.center_x
                        current_bullet.initial_center_y = current_bullet.center_y
                        if i == num_of_tail_segments_plus_point - 1:
                            self.tail_hasnt_started_retracting = False
                    else:
                        # Make all the segments travel off of the screen in a sine wave
                        self.t = self.time_elapsed_since_tail_retraction ** 2
                        if self.tail_retract_positions_not_set:
                            current_bullet.t = -(i * self.distance_between_max_extended_tail_segments) / 107.5
                            if i == num_of_tail_segments_plus_point - 1:
                                self.tail_retract_positions_not_set = False
                        else:
                            current_bullet.t += self.t / 2
                            current_bullet.center_x = self.bullets[0].initial_center_x - (10*((10*current_bullet.t*self.cos_of_tail_angle_in_radians) - (2*math.sin(current_bullet.t) * self.sin_of_tail_angle_in_radians)))
                            current_bullet.center_y = self.bullets[0].initial_center_y - (10*((10*current_bullet.t*self.sin_of_tail_angle_in_radians) + (2*math.sin(current_bullet.t) * self.cos_of_tail_angle_in_radians)))
                        if i == num_of_tail_segments_plus_point - 1:
                            new_tail_point_angle = math.degrees(self.tail_angle_in_radians - math.atan(math.cos(current_bullet.t) / 2) + math.pi)
                            current_bullet.reangle_tail(new_tail_point_angle)
                            self.time_elapsed_since_tail_retraction += delta_time

