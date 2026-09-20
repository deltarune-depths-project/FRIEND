import random

import arcade

from acts import RudinnRedBuster, RudinnDualHeal, RudinnConvince, RudinnLecture
from enemy_attacks import RainingDiamondAttack, CatPounceAttack
from non_player_character import NonPlayerCharacter
from speech_bubble import SpeechBubbleDialog
from sprites_and_effects_collection import SpritesAndEffectsCollection


class Rudinn(NonPlayerCharacter):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection = None, enemies_list: list = [],
                 center_x: float = 0.0, center_y: float = 0.0, bullet_board = None, scale: float = 4.0, angle: float = 0):
        super().__init__(
            sprites_and_effects_collection=sprites_and_effects_collection,
            center_x=center_x,
            center_y=center_y,
            scale=scale,
            angle=angle,
            sprite_folder_name="rudinn",
            name="Rudinn",
            hp=90,
            max_hp=90,
            attack=10,
            defense=2,
            dark_dollars_given_on_defeat=30,
            element_id=0,
            attacks=[
                RainingDiamondAttack(
                    sprites_and_effects_collection=sprites_and_effects_collection,
                    bullet_board=bullet_board,
                    attacker=self,
                    enemies_list=enemies_list
                )
            ],
            acts=[
                RudinnRedBuster(),
                RudinnDualHeal(),
                RudinnConvince(),
                RudinnLecture(enemies_list)
            ],
            enemies_list=enemies_list,
            random_speech_bubble_dialogue=[
                SpeechBubbleDialog(
                    text="Long live the\nguy who pays\nus!",
                    row_count=3,
                    column_count=13,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="I'm just a\nnormal person.",
                    row_count=2,
                    column_count=14,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="Face my\nDiamond\nCutter!",
                    row_count=3,
                    column_count=7,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="Shine,\nshine",
                    row_count=2,
                    column_count=6,
                    actor=self
                )
            ]
        )

        self.bullet_board = bullet_board
        self.battle_description = ("RUDINN - ATK: " + str(self.attack) + " DEF: " + str(self.defense) +
                                   "\nSaid to be someone's best friend, but maybe not.\nShine on, you lazy diamond!")


    def execute_attack(self, enemies: list[NonPlayerCharacter]):
        """
        Executes an attack depending on the number of other enemies in the battle.
        Only execute the Rudinn's attack if it's the first Rudinn on the board.
        Modify the bullet frequency depending on the amount of non-rudinns in the battle.
        :param enemies: The enemies currently present in battle.
        :return: The duration of the attack (in seconds)
        """
        if len(self.attacks) == 0:
            return 10.0
        else:
            attack_index = random.randint(0, len(self.attacks) - 1)
            self.current_attack = self.attacks[attack_index]
            return self.current_attack.execute_attack()


class FRIEND(NonPlayerCharacter):
    def __init__(self, sprites_and_effects_collection: SpritesAndEffectsCollection = None, enemies_list: list = [],
                 center_x: float = 0.0, center_y: float = 0.0, bullet_board = None, scale: float = 4.0, angle: float = 0,
                 soul = None):
        super().__init__(
            sprites_and_effects_collection=sprites_and_effects_collection,
            center_x=center_x,
            center_y=center_y,
            scale=scale,
            angle=angle,
            sprite_folder_name="FRIEND",
            name="FRIEND",
            hp=6666,
            max_hp=6666,
            attack=66,
            defense=66,
            dark_dollars_given_on_defeat=-666,
            element_id=6,
            attacks=[
                #RainingDiamondAttack(
                #    sprites_and_effects_collection=sprites_and_effects_collection,
                #    bullet_board=bullet_board,
                #    attacker=self,
                #    enemies_list=enemies_list
                #),
                CatPounceAttack(
                    sprites_and_effects_collection=sprites_and_effects_collection,
                    attacker=self,
                    soul=soul
                )
            ],
            acts=[
                RudinnRedBuster(),
                RudinnDualHeal(),
                RudinnConvince(),
                RudinnLecture(enemies_list)
            ],
            enemies_list=enemies_list,
            random_speech_bubble_dialogue=[
                SpeechBubbleDialog(
                    text="A BAGFUL OF\nWHITE COTTON",
                    row_count=2,
                    column_count=12,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="ONE THICK\nSEWING NEEDLE",
                    row_count=2,
                    column_count=13,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="LOTS AND\nLOTS OF\nLITTLE PINS",
                    row_count=3,
                    column_count=11,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="A TOMATO MADE\nOF CLOTH",
                    row_count=2,
                    column_count=13,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="TWO YARDS\nOF LEATHER",
                    row_count=2,
                    column_count=10,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="A PAIR OF\nRUSTY SCISSORS",
                    row_count=2,
                    column_count=14,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="A PAIR OF\nBIG BEAUTIFUL\nBUTTONS",
                    row_count=3,
                    column_count=13,
                    actor=self
                ),
                SpeechBubbleDialog(
                    text="A SMALL\nWOODEN TABLE",
                    row_count=2,
                    column_count=12,
                    actor=self
                ),
            ]
        )

        self.speech_bubble_sound = arcade.load_sound("assets/audio/battle/non_player_character/FRIEND/loquatious_cat.mp3")

        self.bullet_board = bullet_board
        self.battle_description = ("FRIEND - ATK: " + str(self.attack) + " DEF: " + str(self.defense) +
                                   "\nYou can't tell how many cats this  counts as.")

        self.animations_by_state["battle_idle"].set_frame_duration(0.3)

    def spawn_speech_bubble_this_turn(self):
        self.speech_bubble_sound.play()
        return super().spawn_speech_bubble_this_turn()

    def execute_attack(self, enemies: list[NonPlayerCharacter]):
        """
        Executes an attack depending on the number of other enemies in the battle.
        Only execute the Rudinn's attack if it's the first Rudinn on the board.
        Modify the bullet frequency depending on the amount of non-rudinns in the battle.
        :param enemies: The enemies currently present in battle.
        :return: The duration of the attack (in seconds)
        """
        if len(self.attacks) == 0:
            return 10.0
        else:
            attack_index = random.randint(0, len(self.attacks) - 1)
            self.current_attack = self.attacks[attack_index]
            return self.current_attack.execute_attack()