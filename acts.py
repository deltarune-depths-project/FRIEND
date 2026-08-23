import arcade
import pyglet.clock

from act import SimpleAct, MagicUserAct, MultiUserAct
from actions import SpellAction
from animations.battle_animations import SoulShiningAnimation
#from player_characters import Susie
from speech_bubble import SpeechBubbleDialog
from spells import RedBuster, HealPrayer, DualHeal


# SimpleActs

class CheckAct(SimpleAct):
    """
    The act associated with the "Check" option in the ACT menu. Displays data about the selected opponent.
    """

    def __init__(self, target, description: str = "Useless analysis"):
        super().__init__(
            name="Check",
            description=description,
            perform_act_text=target.battle_description
        )


class RudinnConvince(SimpleAct):
    def __init__(self):
        super().__init__(
            name="Convince",
            perform_act_text="You told Rudinn to quit fighting.\nIt was utterly swayed.",
            description="Politely persuade enemy",
            mercy_percentage=100
        )

    def perform_act(self, actor, target, controller):
        super().perform_act(actor, target, controller)
        target.assign_speech_bubble_dialog_this_turn(
            SpeechBubbleDialog(
                text="Yeah that\nmakes sense.",
                row_count=2,
                column_count=12,
                actor=target
            )
        )


class RudinnLecture(SimpleAct):
    def __init__(self, enemies_list: list):
        super().__init__(
            name="Lecture",
            perform_act_text="You lectured the enemies on the importance of kindness.\nThe enemies became TIRED...",
            description="Passionately lecture opponents"
        )

        self.enemies_list = enemies_list

    def perform_act(self, actor, target, controller):
        super().perform_act(actor, target, controller)
        for enemy in self.enemies_list:
            enemy.receive_tired(100.0)
            enemy.assign_speech_bubble_dialog_this_turn(
                SpeechBubbleDialog(
                    text="(Yawn)...\nWhat? OK..",
                    row_count=2,
                    column_count=10,
                    actor=enemy
                )
            )


class RudinnRedBuster(MultiUserAct):
    def __init__(self):
        from player_characters import Susie
        super().__init__(
            name="Red Buster",
            perform_act_text="Your SOUL shined its power on Susie!",
            description="Red Damage",
            tp_cost=60,
            additional_actors=[Susie()],
            additional_actors_animation_states=["battle_magic_ready"]
        )

        self.shine_sound = arcade.load_sound(path="assets/audio/battle/snd_boost.wav")

    def perform_act(self, actor, target, controller):
        super().perform_act(actor, target, controller)

        # Play the sound associated with the soul shining.
        pyglet.clock.schedule_once(lambda dt: self.shine_sound.play(), 0.5)

        # Play the soul shining animation.
        soul_shining_animation = SoulShiningAnimation(actor)
        pyglet.clock.schedule_once(
            lambda dt: controller.sprites_and_effects_collection.effects.append(soul_shining_animation),
            0.4
        )
        pyglet.clock.schedule_once(
            lambda dt: controller.sprites_and_effects_collection.effects_sprites.append(soul_shining_animation.sprite),
            0.4
        )


        spell_caster = None
        for player in controller.players:
            if isinstance(player, type(self.additional_actors[0])):
                spell_caster = player
                break

        # Add a SpellAction to the beginning of the actions queue.
        controller.sorted_actions_queue["simple_act_actions"].insert(0,
            SpellAction(
                actor=spell_caster,
                targets=[target],
                spell=RedBuster(),
                controller=controller
            )
        )


class RudinnDualHeal(MultiUserAct):
    def __init__(self):
        from player_characters import Ralsei
        super().__init__(
            name="Dual Heal",
            perform_act_text="Your SOUL shined its power on Ralsei!",
            description="Heals everyone",
            tp_cost=50,
            additional_actors=[Ralsei()],
            additional_actors_animation_states=["battle_magic_ready"]
        )

        self.shine_sound = arcade.load_sound(path="assets/audio/battle/snd_boost.wav")

    def perform_act(self, actor, target, controller):
        super().perform_act(actor, target, controller)

        # Play the sound associated with the soul shining.
        pyglet.clock.schedule_once(lambda dt: self.shine_sound.play(), 0.5)

        # Play the soul shining animation.
        soul_shining_animation = SoulShiningAnimation(actor)
        pyglet.clock.schedule_once(
            lambda dt: controller.sprites_and_effects_collection.effects.append(soul_shining_animation),
            0.4
        )
        pyglet.clock.schedule_once(
            lambda dt: controller.sprites_and_effects_collection.effects_sprites.append(soul_shining_animation.sprite),
            0.4
        )


        spell_caster = None
        for player in controller.players:
            if isinstance(player, type(self.additional_actors[0])):
                spell_caster = player
                break

        # Add a SpellAction to the beginning of the actions queue.

        controller.sorted_actions_queue["simple_act_actions"].insert(0,
            SpellAction(
                actor=spell_caster,
                targets=controller.players,
                spell=DualHeal(),
                controller=controller
            )
        )


# Magic user acts
class NoelleRudinnAction1(MagicUserAct):
    def __init__(self, player):
        from non_player_characters import Rudinn  # TODO: fix this

        super().__init__(
            player=player,
            enemy_type=Rudinn,
            description="Traumatize playing card\nSPARE 50%",
            perform_act_text="Noelle cuts Rudinn card paper snowflakes!\nThey are mortified but impressed!",
            mercy_percentage=50
        )

    def perform_act(self, actor, target, controller):
        super().perform_act(actor, target, controller)
        target.assign_speech_bubble_dialog_this_turn(
            SpeechBubbleDialog(
                text="That's what the\nKnight did to my\ncousin Phil",
                row_count=3,
                column_count=16,
                actor=target
            )
        )

class RalseiRudinnAction1(MagicUserAct):
    def __init__(self, player):
        from non_player_characters import Rudinn

        super().__init__(
            player=player,
            enemy_type=Rudinn,
            description="Offer relief from duty\nSPARE 50%",
            perform_act_text="Ralsei promises that his castle town has suites suited for all suits.",
            mercy_percentage=50
        )

    def perform_act(self, actor, target, controller):
        super().perform_act(actor, target, controller)
        target.assign_speech_bubble_dialog_this_turn(
            SpeechBubbleDialog(
                text="My last house\nwasn't a full\none, but...",
                row_count=3,
                column_count=13,
                actor=target
            )
        )

class SusieRudinnAction1(MagicUserAct):
    def __init__(self, player):
        from non_player_characters import Rudinn

        super().__init__(
            player=player,
            enemy_type=Rudinn,
            description="Wisecrack,\nSPARE 50%",
            perform_act_text="Susie tries to make a joke about UNO and Xboxes.",
            mercy_percentage=30
        )

    def perform_act(self, actor, target, controller):
        super().perform_act(actor, target, controller)
        target.assign_speech_bubble_dialog_this_turn(
            SpeechBubbleDialog(
                text="Oh yeah, never\nheard that one\nbefore...",
                row_count=3,
                column_count=14,
                actor=target
            )
        )
