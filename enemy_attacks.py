import random
from math import atan

import arcade
import pyglet.clock
from arcade import LRBT

import math_methods
import settings
from animations.common_animations import DarknessFootstepAnimation
from bullet_board import BulletBoard
from bullet_patterns import RainingDiamondBulletPattern, CatPounceBulletPattern, PointedTailStabBulletPattern
from enemy_attack import EnemyAttack
from sprites_and_effects_collection import SpritesAndEffectsCollection


class RainingDiamondAttack(EnemyAttack):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, bullet_board: BulletBoard,
                 enemies_list: list, attacker = None, frequency: float = 1.0):
        super().__init__(
            sprites_and_effects_collection=sprites_and_effects_collection,
            duration=10.0
        )

        self.frequency = frequency
        self.bullet_board = bullet_board
        self.attacker = attacker
        self.enemies_list = enemies_list

    def execute_attack(self):
        """
        Starts the attack.
        :return: the duration of the attack
        """
        # Find the number of unique enemy types in battle.
        number_of_unique_enemies_in_battle = get_number_of_unique_enemies_from_enemies_list(self.enemies_list)

        for enemy in self.enemies_list:
            if type(enemy) is type(self.attacker):
                if enemy is self.attacker:
                    raining_diamond_bullet_pattern = RainingDiamondBulletPattern(
                        sprites_and_effects_collection=self.sprites_and_effects_collection,
                        bullet_board=self.bullet_board,
                        frequency=1 / number_of_unique_enemies_in_battle,
                        attacker=self.attacker
                    )
                    self.sprites_and_effects_collection.effects.append(raining_diamond_bullet_pattern)
                    self.bullet_patterns.append(raining_diamond_bullet_pattern)
                else:
                    break

        return 10.0


class CatPounceAttack(EnemyAttack):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, attacker = None, soul = None):
        super().__init__(sprites_and_effects_collection, 10.0)
        self.attacker = attacker
        self.soul = soul

    def execute_attack(self):
        cats_bullet_pattern = CatPounceBulletPattern(
            sprites_and_effects_collection=self.sprites_and_effects_collection,
            soul=self.soul,
            attacker=self.attacker
        )

        self.sprites_and_effects_collection.effects.append(cats_bullet_pattern)
        self.bullet_patterns.append(cats_bullet_pattern)

        return 10.0


class TailJabAttack(EnemyAttack):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection, attacker=None, soul=None):
        super().__init__(sprites_and_effects_collection, 10.0)
        self.attacker = attacker
        self.soul = soul

        self.time = 0.0
        self.rate_of_footsteps_in_seconds = 0.5
        self.number_of_footsteps_between_tail_attack = 4
        self.footsteps_spawned_this_cycle = 0
        self.time_passed_before_attack = 0.0
        self.total_delay_before_attack = .35
        self.time_since_last_footstep_spawn = 0.0
        self.warning_flash_framerate = 0.06

        self.tail_about_to_attack = False

        self.current_footstep_center_x = 0
        self.current_footstep_center_y = 0

        self.position_to_attack_x = 0
        self.position_to_attack_y = 0

        self.inner_footstep_spawn_rect = LRBT(
            left=settings.WINDOW_WIDTH * .1,
            right=settings.WINDOW_WIDTH * .9,
            bottom=settings.WINDOW_HEIGHT * .1,
            top=settings.WINDOW_HEIGHT * .9
        )

        self.outer_footstep_spawn_rect = LRBT(
            left=0,
            right=settings.WINDOW_WIDTH,
            bottom=0,
            top=settings.WINDOW_HEIGHT
        )

        # Sounds
        self.footstep_sound_1 = arcade.load_sound("assets/audio/snd_step1.wav")
        self.footstep_sound_2 = arcade.load_sound("assets/audio/snd_step2.wav")
        self.warning_sound = arcade.load_sound("assets/audio/battle/snd_credit_s.wav")
        self.warning_sound_player = None

    def update_animation(self, delta_time: float):
        self.time += delta_time

        self.time_since_last_footstep_spawn += delta_time
        if self.time_since_last_footstep_spawn > self.rate_of_footsteps_in_seconds:
            self.spawn_footstep_animation()
            random.choice([self.footstep_sound_1.play(), self.footstep_sound_2.play()])
            self.footsteps_spawned_this_cycle += 1
            self.time_since_last_footstep_spawn -= self.rate_of_footsteps_in_seconds

            if self.footsteps_spawned_this_cycle == self.number_of_footsteps_between_tail_attack:
                self.footsteps_spawned_this_cycle = 0
                self.position_to_attack_x = self.soul.center_x
                self.position_to_attack_y = self.soul.center_y
                self.tail_about_to_attack = True

        if self.tail_about_to_attack:
            self.time_passed_before_attack += delta_time

            if self.time_passed_before_attack > self.total_delay_before_attack:
                self.spawn_tail_stab_bullet_pattern()
                self.tail_about_to_attack = False
                self.time_passed_before_attack = 0.0

    def draw(self):
        if self.tail_about_to_attack:
            extended_line = math_methods.extend_line(
                line_points=((self.current_footstep_center_x, self.current_footstep_center_y),
                             (self.position_to_attack_x, self.position_to_attack_y)),
                magnitude=5.0
            )
            if int(self.time_passed_before_attack // self.warning_flash_framerate) % 2 == 0:
                arcade.draw_line(
                    start_x=extended_line[0][0],
                    start_y=extended_line[0][1],
                    end_x=extended_line[1][0],
                    end_y=extended_line[1][1],
                    color=arcade.color.YELLOW,
                    line_width=3
                )
                if self.warning_sound_player:
                    self.warning_sound.stop(self.warning_sound_player)
                self.warning_sound_player = self.warning_sound.play(speed=1.02)
            else:
                arcade.draw_line(
                    start_x=extended_line[0][0],
                    start_y=extended_line[0][1],
                    end_x=extended_line[1][0],
                    end_y=extended_line[1][1],
                    color=arcade.color.RED,
                    line_width=3
                )

    def spawn_tail_stab_bullet_pattern(self):
        tail_stab_bullet_pattern = PointedTailStabBulletPattern(
            sprites_and_effects_collection=self.sprites_and_effects_collection,
            attacker=self.attacker,
            center_x=self.current_footstep_center_x,
            center_y=self.current_footstep_center_y,
            target_x=self.position_to_attack_x,
            target_y=self.position_to_attack_y
        )

        self.sprites_and_effects_collection.effects.append(tail_stab_bullet_pattern)
        self.bullet_patterns.append(tail_stab_bullet_pattern)

    def spawn_footstep_animation(self):
        footstep_spawn_coordinates_not_found = True

        while footstep_spawn_coordinates_not_found:
            center_coords = (random.randrange(settings.WINDOW_WIDTH), random.randrange(settings.WINDOW_HEIGHT))
            if self.outer_footstep_spawn_rect.point_in_rect(center_coords) and not self.inner_footstep_spawn_rect.point_in_rect(center_coords):
                self.current_footstep_center_x = int(center_coords[0])
                self.current_footstep_center_y = int(center_coords[1])
                footstep_spawn_coordinates_not_found = False

        footstep_animation = DarknessFootstepAnimation(
            center_x=self.current_footstep_center_x,
            center_y=self.current_footstep_center_y,
            color=arcade.color.RED
        )

        self.sprites_and_effects_collection.effects.append(footstep_animation)
        self.sprites_and_effects_collection.effects_sprites.append(footstep_animation.sprite)

    def execute_attack(self):
        self.sprites_and_effects_collection.effects.append(self)

        return 10.0

    def terminate_attack(self):
        self.time = 0.0
        self.footsteps_spawned_this_cycle = 0
        self.time_passed_before_attack = 0.0
        self.time_since_last_footstep_spawn = 0.0
        self.tail_about_to_attack = False

        super().terminate_attack()
        if self in self.sprites_and_effects_collection.effects:
             self.sprites_and_effects_collection.effects.remove(self)

def get_number_of_unique_enemies_from_enemies_list(enemies_list: list):
    """
    Get the number of unique enemies in the enemies list.
    :param enemies_list: the enemies list to be checked
    :return: the number of unique enemies in the enemies list
    """
    enemy_types_in_battle = []
    for enemy in enemies_list:
        if type(enemy) not in enemy_types_in_battle:
            enemy_types_in_battle.append(type(enemy))

    return len(enemy_types_in_battle)


