import pygame as pg
import os


class SoundManager:
    def __init__(self):
        pg.mixer.init()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        base = os.path.join(base_dir, "assets", "sounds")

        self.shoot_player = pg.mixer.Sound(os.path.join(base, "player_shoot.ogg"))
        self.player_die = pg.mixer.Sound(os.path.join(base, "player_die.ogg"))

        self.ufo_big_shoot = pg.mixer.Sound(os.path.join(base, "ufo_big_shoot.ogg"))
        self.ufo_big_die = pg.mixer.Sound(os.path.join(base, "ufo_big_die.ogg"))

        self.ufo_small_shoot = pg.mixer.Sound(os.path.join(base, "ufo_small_shoot.ogg"))
        self.ufo_small_die = pg.mixer.Sound(os.path.join(base, "ufo_small_die.ogg"))

        self.asteroid_hit = pg.mixer.Sound(os.path.join(base, "asteroid_hit.ogg"))

        self.shoot_player.set_volume(0.3)
        self.player_die.set_volume(0.6)
        self.ufo_big_shoot.set_volume(0.4)
        self.ufo_big_die.set_volume(0.7)
        self.ufo_small_shoot.set_volume(0.4)
        self.ufo_small_die.set_volume(0.7)
        self.asteroid_hit.set_volume(0.5)
