from math import dist
import pygame
import random

from config import WIDTH, HEIGHT, FPS, BORDER_THICKNESS, TOP_BORDER_THICKNESS
from sprites import Player, DobermannNPC, BlackCatNPC, OrangeCatNPC, Chicken
from sound import SoundManager  # Importamos o novo gerenciador

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Caramel Adventures")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 24)
        self.big_font = pygame.font.SysFont("consolas", 64)

        # Inicializa o Gerenciador de Som
        self.sound_manager = SoundManager()

        # Grupos
        self.all_sprites = pygame.sprite.Group()
        self.chickens = pygame.sprite.Group()

        # Sistema de fases
        self.phase = 1
        self.base_chickens = 4
        self.n_npcs = 11  # 5 dogs + 3 black cats + 3 orange cats

        # Vidas
        self.max_hits = 3
        self.lives = self.max_hits

        # Pontuação
        self.total_score = 0
        self.phase_score = 0

        # PLAYER – spawn fixo
        self.spawn_x = WIDTH // 2
        self.spawn_y = HEIGHT // 2
        self.player = Player(self.spawn_x, self.spawn_y, self.all_sprites)

        # Limites
        self.bounds = pygame.Rect(
            BORDER_THICKNESS,
            TOP_BORDER_THICKNESS,
            WIDTH - 2 * BORDER_THICKNESS,
            HEIGHT - TOP_BORDER_THICKNESS - BORDER_THICKNESS
        )
        self.player.set_bounds(self.bounds)

        # Variável para controlar o cooldown do som de HISS (para não tocar 60x por segundo)
        self.hiss_cooldown = 0 

        # Primeira fase
        self.spawn_phase_entities()

        self.phase_delay = 3.0
        self.waiting_phase_start = True
        self.phase_timer = self.phase_delay

        self.running = True
        self.game_over = False

    # -----------------------------------------------------------
    def random_pos_away_from_player(self, margin, min_distance=150):
        px, py = self.spawn_x, self.spawn_y

        while True:
            left = BORDER_THICKNESS + margin
            right = WIDTH - BORDER_THICKNESS - margin
            top = TOP_BORDER_THICKNESS + margin
            bottom = HEIGHT - BORDER_THICKNESS - margin

            x = random.randint(int(left), int(right))
            y = random.randint(int(top), int(bottom))

            if dist((x, y), (px, py)) >= min_distance:
                return x, y

    # -----------------------------------------------------------
    def respawn_player(self):
        self.player.x = self.spawn_x
        self.player.y = self.spawn_y
        self.player.rect.center = (self.spawn_x, self.spawn_y)

    # -----------------------------------------------------------
    def reset_phase(self):
        """Reinicia a fase atual sem alterar nº da fase, vidas ou pontuação total."""
        self.phase_score = 0  # zera pontuação da fase
        self.respawn_player()
        self.spawn_phase_entities()

        self.waiting_phase_start = True
        self.phase_timer = self.phase_delay

    # -----------------------------------------------------------
    def spawn_phase_entities(self):
        self.all_sprites.empty()
        self.chickens.empty()

        # Player primeiro
        self.all_sprites.add(self.player)

        dogs = self.n_npcs // 3
        blacks = self.n_npcs // 3
        oranges = self.n_npcs - dogs - blacks

        # Dobermanns
        for _ in range(dogs):
            x, y = self.random_pos_away_from_player(80)
            npc = DobermannNPC(x, y, self.all_sprites)
            npc.player = self.player

        # Gatos pretos
        for _ in range(blacks):
            x, y = self.random_pos_away_from_player(60)
            BlackCatNPC(x, y, self.all_sprites)

        # Gatos laranjas
        for _ in range(oranges):
            x, y = self.random_pos_away_from_player(60)
            OrangeCatNPC(x, y, self.all_sprites)

        # Galinhas
        for _ in range(self.base_chickens):
            x, y = self.random_pos_away_from_player(40)
            Chicken(x, y, [self.all_sprites, self.chickens])

        # bounds
        for s in self.all_sprites:
            if hasattr(s, "set_bounds"):
                s.set_bounds(self.bounds)

    # -----------------------------------------------------------
    def next_phase(self):
        self.total_score += self.phase_score  # agrega pontos ganhos
        self.phase_score = 0

        self.phase += 1
        self.n_npcs += 3

        self.respawn_player()
        self.spawn_phase_entities()

        self.waiting_phase_start = True
        self.phase_timer = self.phase_delay

    # -----------------------------------------------------------
    def apply_bark_knockback(self):
        if not self.player.is_barking:
            return

        px, py = self.player.x, self.player.y

        for ent in list(self.all_sprites):
            if ent is self.player or ent in self.chickens:
                continue

            d = dist((px, py), (ent.x, ent.y))
            if d <= 150:
                dx = ent.x - px
                dy = ent.y - py
                mag = max(1, (dx*dx + dy*dy)**0.5)

                new_x = ent.x + (dx / mag) * 150
                new_y = ent.y + (dy / mag) * 150

                bx, by, bw, bh = self.bounds
                new_x = max(bx, min(new_x, bx + bw))
                new_y = max(by, min(new_y, by + bh))

                ent.x = new_x
                ent.y = new_y
                ent.rect.center = (ent.x, ent.y)

    # -----------------------------------------------------------
    def check_cat_proximity_sound(self, dt):
        """Verifica se há algum gato perto para tocar o Hiss"""
        # Diminui o cooldown se ele for maior que 0
        if self.hiss_cooldown > 0:
            self.hiss_cooldown -= dt
        
        # Se ainda estiver em cooldown, não checa nada
        if self.hiss_cooldown > 0:
            return

        px, py = self.player.x, self.player.y
        cat_nearby = False

        for entity in self.all_sprites:
            # Verifica se é instância de gato (Preto ou Laranja)
            if isinstance(entity, BlackCatNPC) or isinstance(entity, OrangeCatNPC):
                d = dist((px, py), (entity.x, entity.y))
                if d < 60:
                    cat_nearby = True
                    break # Se achou um, já basta
        
        if cat_nearby:
            self.sound_manager.play_hiss()
            self.hiss_cooldown = 2.0  # Só toca de novo após 2 segundos para não 'travar' o som

    # -----------------------------------------------------------
    def handle_chicken_collisions(self):
        for chicken in list(self.chickens):
            for entity in self.all_sprites:
                if entity is chicken:
                    continue

                if entity.rect.colliderect(chicken.rect):
                    if isinstance(entity, Player):
                        self.phase_score += 1000
                    chicken.kill()
                    break

        if len(self.chickens) == 0:
            self.next_phase()

    # -----------------------------------------------------------
    def handle_player_entity_collisions(self):
        if self.waiting_phase_start:
            return

        for entity in self.all_sprites:
            if entity is self.player or entity in self.chickens:
                continue

            if entity.rect.colliderect(self.player.rect):

                if not self.player.is_hurt:
                    self.player.hurt()
                    self.lives -= 1
                    
                    # TOCA O SOM DE DANO / REINÍCIO
                    self.sound_manager.play_hurt()

                # sem vidas -> game over
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.reset_phase()   # reinicia a fase atual

                return

    # -----------------------------------------------------------
    def draw_score(self):
        txt = f"{self.total_score + self.phase_score:06d} | Fase {self.phase} | Vidas: {self.lives}"
        surf = self.font.render(txt, True, (255, 255, 255))
        self.screen.blit(surf, (12, 6))

    # -----------------------------------------------------------
    def show_game_over(self):
        text = self.big_font.render("GAME OVER", True, (255, 80, 80))
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(2500)

    # -----------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            # Atualiza sons automáticos (barks e meows a cada 5s)
            self.sound_manager.update()

            if self.game_over:
                self.show_game_over()
                self.running = False
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if not self.waiting_phase_start and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.bark()
                        # TOCA O SOM DO LATIDO DO PLAYER
                        self.sound_manager.play_player_bark()

            # --------------------------------------------------
            #           TELA DE ESPERA DA FASE
            # --------------------------------------------------
            if self.waiting_phase_start:
                self.phase_timer -= dt

                self.screen.fill((30, 30, 30))
                pygame.draw.rect(self.screen, (255,255,255), self.bounds, 2)

                for s in self.all_sprites:
                    self.screen.blit(s.image, s.rect)

                msg = self.font.render(
                    f"Fase {self.phase} começa em {int(self.phase_timer)+1}",
                    True, (255,255,0)
                )
                rect = msg.get_rect(center=(WIDTH//2, HEIGHT//2))
                self.screen.blit(msg, rect)

                self.draw_score()
                pygame.display.flip()

                if self.phase_timer <= 0:
                    self.waiting_phase_start = False
                continue

            # --------------------------------------------------
            #                   GAMEPLAY
            # --------------------------------------------------
            self.apply_bark_knockback()
            self.all_sprites.update(dt)
            
            # Verifica a proximidade dos gatos para o som HISS
            self.check_cat_proximity_sound(dt)
            
            self.handle_chicken_collisions()
            self.handle_player_entity_collisions()

            self.screen.fill((30, 30, 30))
            pygame.draw.rect(self.screen, (255,255,255), self.bounds, 2)
            self.draw_score()
            self.all_sprites.draw(self.screen)
            pygame.display.flip()

        pygame.quit()