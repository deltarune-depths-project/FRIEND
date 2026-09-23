import math
import random

import settings
from bullet_board import BulletBoard
from bullets import Bullet, BlackDiamondBullet, CatBullet, TailCircleBullet, TailPointBullet
from soul import Soul
from sprites_and_effects_collection import SpritesAndEffectsCollection


class BulletPattern:
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, total_duration: float = 10.0,
                 attacker = None):
        self.sprites_and_effects_collection = sprites_and_effects_collection
        self.total_duration = total_duration
        self.attacker = attacker

        self.time = 0
        self.bullets_sprite_list = [] # When spawning a bullet, add it to this list so it can be cleaned up later
        self.total_duration = total_duration
        self.is_terminated = False

    def update_animation(self, delta_time: float):
        self.time += delta_time

        if self.time > self.total_duration:
            self.terminate_animation()

    def terminate_animation(self):
        self.is_terminated = True

        for sprite in self.bullets_sprite_list:
            sprite.kill()
            if sprite in self.sprites_and_effects_collection.effects:
                self.sprites_and_effects_collection.effects.remove(sprite)

    def spawn_bullet(self, bullet: Bullet):
        """
        Add bullets to the bullets sprite list. Also adds the new sprites to the effects sprite list.
        :return: None
        """
        if hasattr(bullet, "get_sprites"):
            for sprite in bullet.get_sprites():
                self.bullets_sprite_list.append(sprite)
                self.sprites_and_effects_collection.bullet_sprites.append(sprite)
        else:
            self.bullets_sprite_list.append(bullet)
            self.sprites_and_effects_collection.bullet_sprites.append(bullet)

        self.sprites_and_effects_collection.effects.append(bullet)

    def spawn_bullets(self, bullets: list[Bullet]):
        """
        Add sprites to the bullets sprite list. Also adds the new sprites to the effects sprite list.
        :return: None
        """

        for bullet in bullets:
            if hasattr(bullet, "get_sprites"):
                for sprite in bullet.get_sprites():
                    self.bullets_sprite_list.append(sprite)
                    self.sprites_and_effects_collection.bullet_sprites.append(sprite)
            else:
                self.bullets_sprite_list.append(bullet)
                self.sprites_and_effects_collection.bullet_sprites.append(bullet)
            self.sprites_and_effects_collection.effects.append(bullet)


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
            self.bullets_sprite_list.pop(0)
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

        self.tail_point = TailPointBullet(
            center_x=int((settings.WINDOW_WIDTH / 3) - 72),
            center_y=int(settings.WINDOW_HEIGHT / 3),
            angle=90,
            sprites_and_effects_collection=sprites_and_effects_collection
        )

        self.spawn_bullet(self.tail_point)

        self.tail_segments = []

        number_of_tail_segments = 10
        for i in range(number_of_tail_segments):
            tail_circle = TailCircleBullet(
                radius=5,
                center_x=int((settings.WINDOW_WIDTH / 3) + (72 * i)),
                center_y=int(settings.WINDOW_HEIGHT / 3),
                sprites_and_effects_collection=sprites_and_effects_collection
            )

            self.tail_segments.append(tail_circle)

        self.spawn_bullets(self.tail_segments)

        # Animation variables
        self.rotation_duration = 2.0
        self.rotation_radius = 20

    def update_animation(self, delta_time: float):
        super().update_animation(delta_time)

        radians = (self.time * math.pi) / 2

        for segment in self.tail_segments:
            segment.center_x = segment.initial_center_x + (self.rotation_radius * math.cos(radians))
            segment.center_y = segment.initial_center_y + (self.rotation_radius * math.sin(radians))
