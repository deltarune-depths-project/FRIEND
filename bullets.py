import arcade
from arcade import Sprite, Texture
from arcade.examples.sprite_health import sprite_off_screen
from arcade.hitbox import HitBox

import settings
from graphics_objects import AnimationState


class Bullet(Sprite):
    def __init__(self, path_or_texture: Texture | str, center_x: float = 0.0, center_y: float = 0.0, angle: float = 0.0,
                 scale: float = 1.0, lifetime: float = 10.0, kill_bullet_when_offscreen: bool = True,
                 base_damage: float = 50.0 ,tp_gain = 0.5, element_id: int = 0, targets_multiple_players: bool = False,
                 attacker = None):
        super().__init__(
            path_or_texture=path_or_texture,
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=scale
        )

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


class CatBullet(Bullet):
    """
    Little cat bullets that interact with the player during the FRIEND fight.
    """

    def __init__(self, center_x: float = 0.0, center_y: float = 0.0, angle: float = 0.0,
                 sprites_and_effects_collection = None, scale: float = 1.0, attacker = None, soul = None):
        super().__init__(
            path_or_texture="assets/sprites/bullets/rudinn_diamond.png",
            center_x=center_x,
            center_y=center_y,
            angle=angle,
            scale=scale,
            attacker=attacker,
            element_id=6
        )

        self.sprites_and_effects_collection = sprites_and_effects_collection
        self.soul = soul

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
                framerate=0.15
            ),
            AnimationState(
                textures=sprites_and_effects_collection.cat_bullet_textures["pouncing"],
                name="pouncing",
                is_looping=True,
                framerate=1.0
            )
        ]

        if sprites_and_effects_collection is not None:
            self.textures = sprites_and_effects_collection.cat_bullet_textures["idle"]
            self.set_texture(0)

        # Variables that control the movement of the cat
        self.minimum_height = int(settings.WINDOW_HEIGHT * .25)
        self.gravity = 1.0 # The acceleration per frame of the sprite

    def update_animation(self, delta_time: float = settings.FRAMERATE):
        return

        if self.is_jumping:
            self.change_y -= self.gravity
        else:
            pass

    def change_state(self, new_state: str = "idle"):
        """
        Changes the state of the cat, as well as its associated animation.
        :param new_state:
        :return:
        """
        for state in self.animation_states:
            if state.name == new_state:
                self.textures = state.textures
                self.set_texture(0)
                break
