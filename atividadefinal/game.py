from math import dist
import pygame
import random

# Importe as cores novas do config
from config import WIDTH, HEIGHT, FPS, BORDER_THICKNESS, TOP_BORDER_THICKNESS, \
    WHITE, BLACK, BUTTON_COLOR, BUTTON_HOVER_COLOR, BACKGROUND_COLOR
from sprites import Player, DobermannNPC, BlackCatNPC, OrangeCatNPC, Chicken
from sound import SoundManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Caramel Adventures")
        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # CARREGAR IMAGEM DE FUNDO
        # ----------------------------------------------------
        try:
            # Tenta carregar a imagem se ela existir na pasta assets
            bg_img = pygame.image.load("assets/background.png").convert()
            # Redimensiona a imagem para caber exatamente na tela do jogo
            self.background = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
            self.has_background = True
        except FileNotFoundError:
            print("AVISO: 'assets/background.png' não encontrado. Usando cor sólida.")
            self.has_background = False

        # ----------------------------------------------------
        # FONTES
        # ----------------------------------------------------
        self.font = pygame.font.SysFont("consolas", 24)
        self.big_font = pygame.font.SysFont("consolas", 64)
        self.title_font = pygame.font.SysFont("consolas", 80, bold=True) # Fonte para o Titulo

        # Inicializa o Gerenciador de Som
        self.sound_manager = SoundManager()

        # Grupos de Sprites
        self.all_sprites = pygame.sprite.Group()
        self.chickens = pygame.sprite.Group()
        self.menu_sprites = pygame.sprite.Group() # Grupo separado para o menu

        # ----------------------------------------------------
        # VARIÁVEIS DO MENU
        # ----------------------------------------------------
        self.in_menu = True # O jogo começa no menu
        self.play_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)
        
        # Player do Menu (Caramel correndo sozinho)
        # manual_control=False faz ele não obedecer o teclado
        self.menu_player = Player(WIDTH//2, HEIGHT//2 - 50, self.menu_sprites, manual_control=False)
        self.menu_player.dx = 1 # Começa correndo para a direita

        # ----------------------------------------------------
        # VARIÁVEIS DO JOGO
        # ----------------------------------------------------
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
        # Player do jogo real (manual_control=True por padrão)
        self.player = Player(self.spawn_x, self.spawn_y, self.all_sprites)

        # Limites da área jogável (cerca)
        self.bounds = pygame.Rect(
            BORDER_THICKNESS,
            TOP_BORDER_THICKNESS,
            WIDTH - 2 * BORDER_THICKNESS,
            HEIGHT - TOP_BORDER_THICKNESS - BORDER_THICKNESS
        )
        self.player.set_bounds(self.bounds)

        # Variável para controlar o cooldown do som de HISS
        self.hiss_cooldown = 0 

        # Inicializa a primeira fase
        self.spawn_phase_entities()

        self.phase_delay = 3.0
        self.waiting_phase_start = True
        self.phase_timer = self.phase_delay

        self.running = True
        self.game_over = False

    # -----------------------------------------------------------
    # HELPERS DO JOGO
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

    def respawn_player(self):
        self.player.x = self.spawn_x
        self.player.y = self.spawn_y
        self.player.rect.center = (self.spawn_x, self.spawn_y)

    def reset_phase(self):
        """Reinicia a fase atual sem alterar nº da fase, vidas ou pontuação total."""
        self.phase_score = 0  # zera pontuação da fase
        self.respawn_player()
        self.spawn_phase_entities()

        self.waiting_phase_start = True
        self.phase_timer = self.phase_delay

    def reset_game(self):
        """Reinicia o jogo do zero (chamado pelo botão Play do menu)"""
        self.phase = 1
        self.lives = self.max_hits
        self.total_score = 0
        self.phase_score = 0
        self.game_over = False
        self.n_npcs = 11
        self.reset_phase()

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

        # Define os limites para todos os sprites
        for s in self.all_sprites:
            if hasattr(s, "set_bounds"):
                s.set_bounds(self.bounds)

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
    # LÓGICA DE GAMEPLAY
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

    def check_cat_proximity_sound(self, dt):
        """Verifica se há algum gato perto para tocar o Hiss"""
        if self.hiss_cooldown > 0:
            self.hiss_cooldown -= dt
        
        if self.hiss_cooldown > 0:
            return

        px, py = self.player.x, self.player.y
        cat_nearby = False

        for entity in self.all_sprites:
            if isinstance(entity, BlackCatNPC) or isinstance(entity, OrangeCatNPC):
                d = dist((px, py), (entity.x, entity.y))
                if d < 60:
                    cat_nearby = True
                    break 
        
        if cat_nearby:
            self.sound_manager.play_hiss()
            self.hiss_cooldown = 2.0 

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
                    self.sound_manager.play_hurt()

                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.reset_phase() 
                return

    # -----------------------------------------------------------
    # DESENHO NA TELA (UI)
    # -----------------------------------------------------------
    def draw_score(self):
        txt = f"{self.total_score + self.phase_score:06d} | Fase {self.phase} | Vidas: {self.lives}"
        surf = self.font.render(txt, True, WHITE)
        self.screen.blit(surf, (12, 6))

    def show_game_over(self):
        # Desenha o fundo antes do texto de Game Over
        if self.has_background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BACKGROUND_COLOR)
            
        text = self.big_font.render("GAME OVER", True, (255, 80, 80))
        rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(text, rect)
        
        # Pequena instrução para voltar ao menu
        subtext = self.font.render("Pressione ESC para o Menu", True, WHITE)
        subrect = subtext.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        self.screen.blit(subtext, subrect)

        pygame.display.flip()
        
        # Loop simples para esperar input no Game Over
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.in_menu = True
                        self.game_over = False
                        waiting = False

    # -----------------------------------------------------------
    # FUNÇÕES DO MENU
    # -----------------------------------------------------------
    def update_menu_animation(self, dt):
        """Faz o Caramel correr de um lado para o outro na tela inicial"""
        # Verifica colisão com as bordas da tela
        if self.menu_player.x > WIDTH - 50:
            self.menu_player.dx = -1 # Vira para esquerda
        elif self.menu_player.x < 50:
            self.menu_player.dx = 1  # Vira para direita
        
        # Atualiza a animação do sprite do menu
        self.menu_sprites.update(dt)

    def draw_menu(self):
        # 1. Desenha o Fundo
        if self.has_background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BACKGROUND_COLOR)

        # 2. Título do Jogo
        title_surf = self.title_font.render("Caramel Adventures", True, (255, 165, 0)) # Laranja Caramelo
        # Adiciona uma sombra simples ao título para destacar do fundo
        title_shadow = self.title_font.render("Caramel Adventures", True, BLACK)
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 150))
        self.screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title_surf, title_rect)

        # 3. Desenha o Caramel do Menu
        self.menu_sprites.draw(self.screen)

        # 4. Botão de Play
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER_COLOR if self.play_button.collidepoint(mouse_pos) else BUTTON_COLOR
        
        pygame.draw.rect(self.screen, color, self.play_button, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, self.play_button, 2, border_radius=12) # Borda branca

        play_text = self.big_font.render("JOGAR", True, WHITE)
        play_rect = play_text.get_rect(center=self.play_button.center)
        self.screen.blit(play_text, play_rect)

        # 5. Créditos (Nomes) com sombra para leitura
        credits_text = "Criado por: Ranielly Barroso & Luiza Batista"
        credits_surf = self.font.render(credits_text, True, WHITE)
        credits_shadow = self.font.render(credits_text, True, BLACK)
        credits_rect = credits_surf.get_rect(center=(WIDTH//2, HEIGHT - 80))
        self.screen.blit(credits_shadow, (credits_rect.x+1, credits_rect.y+1))
        self.screen.blit(credits_surf, credits_rect)

        # 6. Universidade com sombra
        uni_text = "EST - UEA"
        uni_surf = self.font.render(uni_text, True, (200, 200, 200))
        uni_shadow = self.font.render(uni_text, True, BLACK)
        uni_rect = uni_surf.get_rect(center=(WIDTH//2, HEIGHT - 40))
        self.screen.blit(uni_shadow, (uni_rect.x+1, uni_rect.y+1))
        self.screen.blit(uni_surf, uni_rect)

        pygame.display.flip()

    # -----------------------------------------------------------
    # LOOP PRINCIPAL
    # -----------------------------------------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.sound_manager.update()

            # ==================================================
            # ESTADO: MENU
            # ==================================================
            if self.in_menu:
                self.update_menu_animation(dt)
                self.draw_menu()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: # Clique esquerdo
                            if self.play_button.collidepoint(event.pos):
                                self.in_menu = False
                                self.reset_game() # Começa o jogo do zero
                continue

            # ==================================================
            # ESTADO: GAME OVER
            # ==================================================
            if self.game_over:
                self.show_game_over()
                continue

            # ==================================================
            # ESTADO: JOGO RODANDO
            # ==================================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Atalho para voltar ao menu (Tecla ESC)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.in_menu = True

                if not self.waiting_phase_start and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.bark()
                        self.sound_manager.play_player_bark()

            # --- Tela de Espera entre Fases ---
            if self.waiting_phase_start:
                self.phase_timer -= dt

                # Desenha o fundo
                if self.has_background:
                    self.screen.blit(self.background, (0, 0))
                else:
                    self.screen.fill(BACKGROUND_COLOR)

                # Desenha a cerca e os sprites estáticos
                pygame.draw.rect(self.screen, WHITE, self.bounds, 2)
                for s in self.all_sprites:
                    self.screen.blit(s.image, s.rect)

                # Mensagem de contagem regressiva
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

            # --- Gameplay Real (Sprites se mexendo) ---
            self.apply_bark_knockback()
            self.all_sprites.update(dt)
            self.check_cat_proximity_sound(dt)
            self.handle_chicken_collisions()
            self.handle_player_entity_collisions()

            # Desenha o fundo
            if self.has_background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(BACKGROUND_COLOR)

            # Desenha a cerca, score e sprites
            pygame.draw.rect(self.screen, WHITE, self.bounds, 2)
            self.draw_score()
            self.all_sprites.draw(self.screen)
            pygame.display.flip()

        pygame.quit()