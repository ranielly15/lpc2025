import math
from random import uniform

import pygame as pg

import config as C
from sprites import Asteroid, Ship, UFO, Bullet
from utils import Vec, rand_edge_pos, rand_unit_vec


class World:

    def __init__(self, sound):
        self.sound = sound
        self.reset()

    def reset(self):

        self.ship = Ship((C.WIDTH / 2, C.HEIGHT / 2))
        self.bullets = pg.sprite.Group()
        self.ufo_bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group(self.ship)

        self.score = 0
        self.lives = C.START_LIVES
        self.wave = 0
        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.ufo_timer = C.UFO_SPAWN_EVERY

        self.start_wave()

        self.game_over = False

    def start_wave(self):
        self.wave += 1
        count = 3 + self.wave
        for _ in range(count):
            pos = rand_edge_pos()
            while (pos - self.ship.pos).length() < 150:
                pos = rand_edge_pos()
            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            self.spawn_asteroid(pos, vel, "L")

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str):
        a = Asteroid(pos, vel, size)
        self.asteroids.add(a)
        self.all_sprites.add(a)

    def spawn_ufo(self):
        small = uniform(0, 1) < 0.5
        y = uniform(0, C.HEIGHT)
        x = 0 if uniform(0, 1) < 0.5 else C.WIDTH
        ufo = UFO(Vec(x, y), small)
        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    def try_fire(self):
        if len(self.bullets) >= C.MAX_BULLETS:
            return
        b = self.ship.fire()
        if b:
            self.bullets.add(b)
            self.all_sprites.add(b)

            if hasattr(self.sound, "shoot_player"):
                self.sound.shoot_player.play()

    def hyperspace(self):
        self.ship.hyperspace()
        self.score = max(0, self.score - C.HYPERSPACE_COST)

    def update(self, dt: float, keys):

        self.ship.control(keys, dt)
        self.ship.update(dt)

        for b in list(self.bullets):
            b.update(dt)
        for b in list(self.ufo_bullets):
            b.update(dt)
        for a in list(self.asteroids):
            a.update(dt)
        for u in list(self.ufos):
            u.update(dt)

        if self.safe > 0:
            self.safe -= dt
            self.ship.invuln = 0.5

        self.ufo_timer -= dt
        if self.ufo_timer <= 0:
            self.spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        for ufo in list(self.ufos):
            if getattr(ufo, "small", False):
                if hasattr(ufo, "_update_small_ufo_movement"):
                    ufo._update_small_ufo_movement(dt, self.ship.pos)

        for ufo in list(self.ufos):
            shot = ufo.fire(self.ship.pos)
            if shot:
                self.ufo_bullets.add(shot)
                self.all_sprites.add(shot)

                if hasattr(self.sound, "ufo_small_shoot") and ufo.small:
                    self.sound.ufo_small_shoot.play()
                elif hasattr(self.sound, "ufo_big_shoot") and not ufo.small:
                    self.sound.ufo_big_shoot.play()

        self.handle_collisions()

        if not self.asteroids and self.wave_cool <= 0:
            self.start_wave()
            self.wave_cool = C.WAVE_DELAY
        elif not self.asteroids:
            self.wave_cool -= dt

    def handle_collisions(self):

        hits = pg.sprite.groupcollide(
            self.asteroids,
            self.bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in hits.items():
            self.split_asteroid(ast)
            if hasattr(self.sound, "asteroid_hit"):
                self.sound.asteroid_hit.play()

        for ufo in list(self.ufos):
            for b in list(self.bullets):
                if (ufo.pos - b.pos).length() < (ufo.r + b.r):
                    score = C.UFO_SMALL["score"] if ufo.small else C.UFO_BIG["score"]
                    self.score += score
                    ufo.kill()
                    b.kill()
                    if ufo.small and hasattr(self.sound, "ufo_small_die"):
                        self.sound.ufo_small_die.play()
                    elif not ufo.small and hasattr(self.sound, "ufo_big_die"):
                        self.sound.ufo_big_die.play()

        for ast in list(self.asteroids):
            for ufo in list(self.ufos):
                if (ast.pos - ufo.pos).length() < (ast.r + ufo.r):
                    ufo.kill()

                    if ufo.small and hasattr(self.sound, "ufo_small_die"):
                        self.sound.ufo_small_die.play()
                    elif not ufo.small and hasattr(self.sound, "ufo_big_die"):
                        self.sound.ufo_big_die.play()
                    break

        if self.ship.invuln <= 0 and self.safe <= 0:
            for b in list(self.ufo_bullets):
                if (b.pos - self.ship.pos).length() < (b.r + self.ship.r):
                    b.kill()
                    self.ship_die()
                    break

        if self.ship.invuln <= 0 and self.safe <= 0:
            for ast in self.asteroids:
                if (ast.pos - self.ship.pos).length() < (ast.r + self.ship.r):
                    self.ship_die()
                    break

        if self.ship.invuln <= 0 and self.safe <= 0:
            for ufo in self.ufos:
                if (ufo.pos - self.ship.pos).length() < (ufo.r + self.ship.r):
                    self.ship_die()
                    break

    def split_asteroid(self, ast: Asteroid):
        self.score += C.AST_SIZES[ast.size]["score"]
        split = C.AST_SIZES[ast.size]["split"]
        pos = Vec(ast.pos)
        ast.kill()
        for s in split:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self.spawn_asteroid(pos, dirv * speed, s)

    def ship_die(self):

        if hasattr(self.sound, "player_die"):
            self.sound.player_die.play()

        self.lives -= 1

        self.ship.respawn()
        self.safe = C.SAFE_SPAWN_TIME

        if self.lives < 0:
            self.game_over = True

    def draw(self, surf: pg.Surface, font: pg.font.Font = None):

        for a in self.asteroids:
            a.draw(surf)
        for u in self.ufos:
            u.draw(surf)
        for b in self.bullets:
            b.draw(surf)
        for b in self.ufo_bullets:
            b.draw(surf)
        self.ship.draw(surf)

        if font is not None:
            pg.draw.line(surf, (60, 60, 60), (0, 50), (C.WIDTH, 50), width=1)
            txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
            label = font.render(txt, True, C.WHITE)
            surf.blit(label, (10, 10))
