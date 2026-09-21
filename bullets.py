import math
import random

import arcade
from arcade import Sprite, Texture, SpriteCircle
from arcade.examples.sprite_health import sprite_off_screen
from arcade.hitbox import HitBox

import settings
from graphics_objects import AnimationState
from enum import Enum, auto

from sprites_and_effects_collection import SpritesAndEffectsCollection


class Bullet(Sprite):
    def __init__(self, path_or_texture: Texture | str, center_x: float = 0.0, center_y: float = 0.0, angle: float = 0.0,
                 scale: float = 1.0, lifetime: float = 10.0, kill_bullet_when_offscreen: bool = True,
                 base_damage: float = 50.0 ,tp_gain = 0.5, element_id: int = 0, targets_multiple_players: bool = False,
                 attacker = None, sprites_and_effects_collection: SpritesAndEffectsCollection = None):
        super().__init__(
            path_or_texture=path_or_texture,
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=scale
        )

        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.time = 0.0
        self.lifetime = lifetime
        self.kill_bullet_when_offscreen = kill_bullet_when_offscreen
        self.base_damage = base_damage # The base damage that the bullet should deal to its target.
        if attacker is not None:
            self.damage = self.base_damage + (attacker.attack * 3)
        else:
            self.damage = self.base_damage
        self.tp_gain_when_grazed = tp_gain  # The amount of TP gained when the soul grazes the bullet
        self.has_been_grazed = False  # Whether the bullet has been grazed yet
        self.element_id = element_id # The element ID of the bullet. Defaults to 0
        self.targets_multiple_players = targets_multiple_players # Determines if the bullet should damage multiple players

        self.lower_limit = -self.height
        self.upper_limit = settings.WINDOW_HEIGHT + self.height
        self.left_limit = -self.width
        self.right_limit = settings.WINDOW_WIDTH + self.width

class CircleBullet(SpriteCircle):
    def __init__(self, radius: int = 10, color: tuple[int, int, int, int] = (0, 0, 0, 255), soft: bool = False,
                 center_x: float = 0.0, center_y: float = 0.0, lifetime: float = 10.0,
                 kill_bullet_when_offscreen: bool = True, base_damage: float = 50.0, tp_gain=0.5, element_id: int = 0,
                 targets_multiple_players: bool = False, attacker = None,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None):
        super().__init__(
            radius=radius,
            color=color,
            soft=soft,
            center_x=center_x,
            center_y=center_y
        )

        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.time = 0.0
        self.lifetime = lifetime
        self.kill_bullet_when_offscreen = kill_bullet_when_offscreen
        self.base_damage = base_damage  # The base damage that the bullet should deal to its target.
        if attacker is not None:
            self.damage = self.base_damage + (attacker.attack * 3)
        else:
            self.damage = self.base_damage
        self.tp_gain_when_grazed = tp_gain  # The amount of TP gained when the soul grazes the bullet
        self.has_been_grazed = False  # Whether the bullet has been grazed yet
        self.element_id = element_id  # The element ID of the bullet. Defaults to 0
        self.targets_multiple_players = targets_multiple_players  # Determines if the bullet should damage multiple players

        self.lower_limit = -self.height
        self.upper_limit = settings.WINDOW_HEIGHT + self.height
        self.left_limit = -self.width
        self.right_limit = settings.WINDOW_WIDTH + self.width

    def update_animation(self, delta_time: float = 1 / 60):
        self.time += delta_time

        # Kills the bullet if it goes offscreen if the bullet is configured to be killed offscreen.
        if self.kill_bullet_when_offscreen:
            if self.top < self.lower_limit or self.bottom > self.upper_limit or self.right < self.left_limit or self.left > self.right_limit:
                self.kill()

        # Kills the bullet if it is on screen for longer than the bullets designated lifetime.
        if self.time > self.lifetime:
            self.kill()

    def update_animation(self, delta_time: float = 1 / 60):
        self.time += delta_time

        # Kills the bullet if it goes offscreen if the bullet is configured to be killed offscreen.
        if self.kill_bullet_when_offscreen:
            if self.top < self.lower_limit or self.bottom > self.upper_limit or self.right < self.left_limit or self.left > self.right_limit:
                self.kill()

        # Kills the bullet if it is on screen for longer than the bullets designated lifetime.
        if self.time > self.lifetime:
            self.kill()

class BlackDiamondBullet(Bullet):
    """
    The black diamond bullet. Used a lot in Chapter 1, primarily by Rudinns but also by enemies like Jevil.
    """
    def __init__(self, center_x: float = 0.0, center_y: float = 0.0, angle: float = 0.0, scale: float = 2.0,
                 attacker = None):
        super().__init__(
            path_or_texture="assets/sprites/bullets/rudinn_diamond.png",
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=scale,
            attacker=attacker
        )

        self.initial_center_x = center_x
        self.initial_center_y = center_y

        self.hit_box = HitBox(
            points=[
                (-4.14, -10.0),
                ( 4.14, -10.0),
                (10.0, -4.14),
                (10.0,  4.14),
                ( 4.14, 10.0),
                (-4.14, 10.0),
                (-10.0,  4.14),
                (-10.0, -4.14),
            ]
        )

        self.alpha = 0

    def update_animation(self, delta_time: float = 1 / 60):
        super().update_animation(delta_time)
        if self.alpha < 255:
            self.alpha = min(self.alpha + (delta_time * 512), 255)

        self.center_y = self.center_y - (2 * (self.time ** 2) - 1)


class CatState(Enum):
    IDLE = auto()
    WALKING = auto()
    POUNCING = auto()
    DANCING = auto()

class CatBullet(Bullet):
    """
    Little cat bullets that interact with the player during the FRIEND fight.
    """

    def __init__(self, sprites_and_effects_collection, center_x: float = 0.0, center_y: float = 0.0, angle: float = 0.0,
                scale: float = 3.0, attacker = None, soul = None):
        super().__init__(
            path_or_texture="assets/sprites/bullets/rudinn_diamond.png",
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=scale,
            attacker=attacker,
            element_id=6,
            tp_gain=4.0
        )

        self.sprites_and_effects_collection = sprites_and_effects_collection
        self.soul = soul

        self.jump_sound = arcade.load_sound("assets/audio/battle/snd_jump.wav")
        self.meow_sound = arcade.load_sound("assets/audio/battle/non_player_character/FRIEND/snd_meow.wav")

        self.animation_states = [
            AnimationState(
                textures=sprites_and_effects_collection.cat_bullet_textures["idle"],
                name="idle",
                is_looping=True,
                framerate=1.0
            ),
            AnimationState(
                textures=sprites_and_effects_collection.cat_bullet_textures["walking"],
                name="walking",
                is_looping=True,
                framerate=0.2
            ),
            AnimationState(
                textures=sprites_and_effects_collection.cat_bullet_textures["dancing"],
                name="dancing",
                is_looping=True,
                framerate=0.06
            ),
            AnimationState(
                textures=sprites_and_effects_collection.cat_bullet_textures["pouncing"],
                name="pouncing",
                is_looping=True,
                framerate=999.0
            )
        ]

        self.current_animation_state = self.animation_states[0]

        self.state = CatState.IDLE

        self.valid_states = {
            "idle": CatState.IDLE,
            "walking": CatState.WALKING,
            "dancing": CatState.DANCING,
            "pouncing": CatState.POUNCING
        }

        if sprites_and_effects_collection is not None:
            self.textures = sprites_and_effects_collection.cat_bullet_textures["idle"]
            self.set_texture(0)

        # Internal variables used to track the animation of the cat
        self.texture_animation_clock = 0.0
        self.current_texture_index = 0

        # Variables that control the movement of the cat
        self.normalized_center_x = self.center_x
        self.normalized_center_y = self.center_y
        self.minimum_height = int(settings.WINDOW_HEIGHT / 3)  # The "floor" that the cat walks and lands on
        self.gravity = 0.5 # The acceleration per frame of the sprite
        self.jump_velocity = 20.0 # The velocity of the cat's jump
        self.duration_between_landing_and_jumping = 1.0  # The amount of time before the next jump in seconds
        self.seconds_before_next_jump = self.duration_between_landing_and_jumping - (random.random() - 0.5)
        self.change_x = -2.5
        self.cat_has_not_jumped = True
        self.soul_is_to_the_left_of_cat = True

    def update_animation(self, delta_time: float = settings.FRAMERATE):
        match self.state:
            case CatState.POUNCING:
                self.change_y -= self.gravity
                # If the game catches that the cat has landed, return its state to walking
                if self.bottom < self.minimum_height:
                    self.center_y = self.minimum_height + self.height / 2
                    self.change_state("idle")
                    self.seconds_before_next_jump = self.duration_between_landing_and_jumping
                    self.change_x = -2.5
                    self.normalized_center_x = self.center_x
                    self.change_y = 0.0
            case CatState.IDLE:
                self.normalized_center_x -= 2.5
                dx = self.soul.center_x - self.center_x
                horizontal_distance = abs(dx)
                if horizontal_distance <= 200:
                    self.seconds_before_next_jump -= delta_time
                    if self.seconds_before_next_jump <= 0:  # and self.cat_has_not_jumped:
                        self.jump()
                    else:
                        if self.cat_has_not_jumped:
                            # vibrate the cat
                            self.center_x = self.normalized_center_x + ((random.random() - .5) * ((2.0 - self.seconds_before_next_jump) * 5))
                            self.center_y = self.normalized_center_y + ((random.random() - .5) * ((2.0 - self.seconds_before_next_jump) * 5))
                if dx < 0 and self.soul_is_to_the_left_of_cat:
                    self.scale_x = -self.scale_x
                    self.soul_is_to_the_left_of_cat = False
                elif dx > 0 and not self.soul_is_to_the_left_of_cat:
                    self.scale_x = -self.scale_x
                    self.soul_is_to_the_left_of_cat = True
                if self.center_x < 250 or self.center_x > settings.WINDOW_WIDTH - 250:
                    self.change_state("dancing")
            case CatState.DANCING:
                self.normalized_center_x -= 2.5
                horizontal_distance = abs(self.soul.center_x - self.center_x)
                if horizontal_distance <= 250:
                    self.change_state("idle")


        self.update(delta_time)

        self.texture_animation_clock += delta_time
        if self.texture_animation_clock >= self.current_animation_state.get_framerate():
            self.texture_animation_clock -= self.current_animation_state.get_framerate()
            if self.current_texture_index < len(self.textures) - 1:
                self.current_texture_index += 1
            else:
                self.current_texture_index = 0
            self.set_texture(self.current_texture_index)

    def change_state(self, new_state: str = "idle"):
        """
        Changes the state of the cat, as well as its associated animation.
        :param new_state:
        :return:
        """
        # print(new_state)

        for state in self.animation_states:
            if state.name == new_state:
                self.textures = state.textures
                if new_state == "pouncing":
                    self.set_texture(random.randint(0, len(self.textures) - 1))
                else:
                    self.set_texture(0)
                self.current_animation_state = state
                break

        if new_state in self.valid_states:
            self.state = self.valid_states[new_state]

        self.texture_animation_clock = 0.0

    def jump(self):
        """
        Makes the cat jump.
        :return: None
        """

        self.cat_has_not_jumped = False

        # Change the state of the cat to pouncing
        self.change_state("pouncing")

        # Play the jump sounds.
        self.jump_sound.play(speed=2.0, volume=0.5)
        self.meow_sound.play(speed=1.0 + (random.random()), volume=0.75)

        # Calculate the change in trajectory of the cat
        dx = self.soul.center_x - self.center_x
        dy = self.soul.center_y - self.center_y

        angle = math.atan2(dy, dx)

        dvx = self.jump_velocity * math.cos(angle)
        dvy = self.jump_velocity * math.sin(angle)

        self.change_x = dvx
        self.change_y = dvy

        self.cat_has_not_jumped = False


class TailCircleBullet(CircleBullet):
    def __init__(self, radius: int = 10, center_x: int = 0, center_y: int = 0,
                 sprites_and_effects_collection: SpritesAndEffectsCollection = None):
        super().__init__(
            radius=radius,
            color=(0, 0, 0, 0),
            center_x=center_x,
            center_y=center_y,
            element_id=6,
            tp_gain=2.0
        )

        self.sprites_and_effects_collection = sprites_and_effects_collection

        self.scale = 4.0

        self.black_circle = SpriteCircle(
            radius=radius,
            color=arcade.color.BLACK,
            center_x=center_x,
            center_y=center_y
        )

        self.black_circle.scale = 4.0

        self.background_circle = SpriteCircle(
            radius=radius + 2,
            color=arcade.color.WHITE,
            center_x=center_x,
            center_y=center_y
        )

        self.background_circle.scale = 4.0

        self.starting_radius = radius

    def update_animation(self, delta_time: float):
        self.time += delta_time

        new_radius = int(self.starting_radius + (math.sin(self.time) * 5))

        new_black_circle = SpriteCircle(
            radius=new_radius,
            color=arcade.color.BLACK,
            center_x=self.center_x,
            center_y=self.center_y
        )

        new_black_circle.scale = 4

        new_background_circle = SpriteCircle(
            radius=new_radius + 2,
            color=arcade.color.WHITE,
            center_x=self.center_x,
            center_y=self.center_y
        )

        new_background_circle.scale = 4

        for i in range(len(self.sprites_and_effects_collection.bullet_sprites)):
            if self.sprites_and_effects_collection.bullet_sprites[i] is self.background_circle:
                self.background_circle = new_background_circle
                self.sprites_and_effects_collection.bullet_sprites[i] = self.background_circle
            if self.sprites_and_effects_collection.bullet_sprites[i] is self.black_circle:
                self.black_circle = new_black_circle
                self.sprites_and_effects_collection.bullet_sprites[i] = self.black_circle
                break

    def get_sprites(self):
        return [self.background_circle, self.black_circle, self]
