import pygame as pg
from systems import World
from sound import SoundManager
import config as C

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Asteroids")

        self.clock = pg.time.Clock()
        self.font_small = pg.font.SysFont("consolas", 20)
        self.font_big = pg.font.SysFont("consolas", 48)

        try:
            self.sound = SoundManager()
        except Exception:
            self.sound = None

        self.world = World(self.sound)

        self.running = True
        self.state = "start"     

    def run(self):
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            self.handle_events()

            if self.state == "start":
                self.draw_start_screen()

            elif self.state == "playing":
                keys = pg.key.get_pressed()
                self.world.update(dt, keys)
    
                if getattr(self.world, "game_over", False):
                    self.state = "gameover"
                self.draw_game()

            elif self.state == "gameover":
                self.draw_gameover()

            pg.display.flip()

        pg.quit()

    def draw_start_screen(self):
        self.screen.fill(C.BLACK)
        text = self.font_big.render("ASTEROIDS", True, C.WHITE)
        text2 = self.font_small.render("Maria Luiza Pereira Batista", True, C.WHITE)
        text3 = self.font_small.render("Ranielly Jennifer Barroso Salvador", True, C.WHITE)
        prompt = self.font_small.render("Press SPACE to start", True, C.GRAY)
        self.screen.blit(text, (C.WIDTH // 2 - text.get_width() // 2, 200))
        self.screen.blit(text2, (C.WIDTH // 2 - text.get_width() // 2, 500))
        self.screen.blit(text3, (C.WIDTH // 2 - text.get_width() // 2, 550))
        self.screen.blit(prompt, (C.WIDTH // 2 - prompt.get_width() // 2, 300))

    def draw_game(self):
        self.screen.fill(C.BLACK)
        self.world.draw(self.screen, self.font_small)

    def draw_gameover(self):
        self.screen.fill(C.BLACK)
        text = self.font_big.render("GAME OVER", True, (255, 80, 80))
        score = self.font_small.render(f"SCORE {self.world.score:06d}", True, C.WHITE)
        prompt = self.font_small.render("Press SPACE to restart", True, C.GRAY)

        self.screen.blit(text, (C.WIDTH // 2 - text.get_width() // 2, 200))
        self.screen.blit(score, (C.WIDTH // 2 - score.get_width() // 2, 300))
        self.screen.blit(prompt, (C.WIDTH // 2 - prompt.get_width() // 2, 350))

    def handle_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False
            elif e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                self.running = False
            elif e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                if self.state == "start":
                    self.state = "playing"
                elif self.state == "gameover":
                   
                    self.world.reset()
                    self.state = "playing"
                elif self.state == "playing":
                   
                    self.world.try_fire()
            elif e.type == pg.KEYDOWN and e.key == pg.K_LSHIFT:
                if self.state == "playing":
                    self.world.hyperspace()
