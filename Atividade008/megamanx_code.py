import pygame
import os

# --- 1. Inicialização e Configurações da Tela ---
pygame.init()

LARGURA_TELA = 800
ALTURA_TELA = 600
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Meu Mega Man X")

# Cor de fundo
PRETO = (0, 0, 0)
# Cor Rosa (para transparência, baseado nas suas imagens)
MAGENTA = (255, 0, 255)

# Controle de FPS (Frames Por Segundo)
clock = pygame.time.Clock()
FPS = 60

# --- 2. Classe do Jogador (Mega Man X) ---
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        """ Método construtor - chamado uma vez quando o Jogador é criado. """
        super().__init__()
        
        # ### CONTROLE DE TAMANHO ###
        # Defina o quanto você quer aumentar o personagem.
        # 2.0 = Dobro do tamanho
        # 2.5 = 2.5x o tamanho
        # 3.0 = Triplo do tamanho
        self.escala = 4.5 
        
        # --- Carregamento dos Sprites ---
        
        self.anim_parado = []
        for i in range(1, 4): # Carrega parado1.png, parado2.png, parado3.png
            arquivo = f"parado{i}.png"
            imagem = pygame.image.load(os.path.join("sprites", arquivo)).convert()
            imagem.set_colorkey(MAGENTA)
            
            # --- Bloco de Escala ---
            largura_original = imagem.get_width()
            altura_original = imagem.get_height()
            nova_largura = int(largura_original * self.escala)
            nova_altura = int(altura_original * self.escala)
            imagem_escalada = pygame.transform.scale(imagem, (nova_largura, nova_altura))
            
            # Adiciona a imagem JÁ ESCALADA na lista
            self.anim_parado.append(imagem_escalada) 
            
        self.anim_correndo = []
        for i in range(1, 12): # Carrega correndo1.png a correndo11.png
            arquivo = f"correndo{i}.png"
            imagem = pygame.image.load(os.path.join("sprites", arquivo)).convert()
            imagem.set_colorkey(MAGENTA)
            
            # --- Bloco de Escala ---
            largura_original = imagem.get_width()
            altura_original = imagem.get_height()
            nova_largura = int(largura_original * self.escala)
            nova_altura = int(altura_original * self.escala)
            imagem_escalada = pygame.transform.scale(imagem, (nova_largura, nova_altura))
            
            self.anim_correndo.append(imagem_escalada)

        self.anim_pulando = []
        for i in range(1, 7): # Carrega pulando1.png a pulando6.png
            arquivo = f"pulando{i}.png"
            imagem = pygame.image.load(os.path.join("sprites", arquivo)).convert()
            imagem.set_colorkey(MAGENTA)
            
            # --- Bloco de Escala ---
            largura_original = imagem.get_width()
            altura_original = imagem.get_height()
            nova_largura = int(largura_original * self.escala)
            nova_altura = int(altura_original * self.escala)
            imagem_escalada = pygame.transform.scale(imagem, (nova_largura, nova_altura))

            self.anim_pulando.append(imagem_escalada)

        # Lista de atirando (vazia por enquanto)
        self.anim_atirando = []

        # --- Variáveis de Estado e Animação ---
        self.frame_atual = 0 
        self.image = self.anim_parado[self.frame_atual] # Imagem inicial
        self.rect = self.image.get_rect() # Retângulo (posição/colisão)
        
        # --- Posição e Física ---
        self.rect.x = 100 # Posição inicial X
        self.rect.y = 400 # Posição inicial Y (começa no ar e cai)
        self.vel_x = 0     # Velocidade horizontal
        self.vel_y = 0     # Velocidade vertical
        self.gravidade = 0.8  # Força da gravidade
        self.forca_pulo = -15 # Força do pulo (negativo é para cima)
        
        # --- Flags (Bandeiras) de Estado ---
        self.pulando = True # Começa 'True' para ele cair no chão
        self.correndo = False
        self.atirando = False
        self.olhando_direita = True # Para onde o sprite está virado
        
        # --- Controle de Tempo da Animação ---
        self.ultimo_update = pygame.time.get_ticks()
        # Velocidade da animação (em milissegundos)
        self.velocidade_anim = 90 # Ajuste se achar rápido ou devagar.

    def update(self):
        """ Atualiza a lógica do jogador a cada frame (60 vezes por segundo). """
        
        # --- 1. Física e Gravidade ---
        self.vel_y += self.gravidade
        self.rect.y += self.vel_y
        
        # --- 2. Simulação do "Chão" ---
        chao = 500 # Posição Y do chão. Ajuste este valor!
        if self.rect.bottom > chao:
            self.rect.bottom = chao
            self.vel_y = 0
            self.pulando = False

        # --- 3. Movimento Horizontal ---
        self.rect.x += self.vel_x
        
        # --- 4. Seleção de Animação (Máquina de Estado) ---
        estado_anim = self.anim_parado
        
        if self.pulando:
            estado_anim = self.anim_pulando
        elif self.atirando:
            # Se a lista de atirar não estiver vazia, usa ela
            if self.anim_atirando:
                estado_anim = self.anim_atirando
            else:
                # Senão, usa 'parado' como substituto
                estado_anim = self.anim_parado 
        elif self.correndo:
            estado_anim = self.anim_correndo
            
        # --- 5. Chamar a função de Animar ---
        self.animar(estado_anim)

    def animar(self, lista_animacao):
        """ Controla a troca de frames (imagens). """
        agora = pygame.time.get_ticks()
        
        # Verifica se já passou tempo suficiente para o próximo frame
        if agora - self.ultimo_update > self.velocidade_anim:
            self.ultimo_update = agora
            
            # Avança para o próximo frame
            self.frame_atual = (self.frame_atual + 1) % len(lista_animacao)
            
            # Pega a nova imagem da lista de animação
            imagem_nova = lista_animacao[self.frame_atual]
            
            # Preserva o centro do personagem para a animação não "pular" de lugar
            centro_antigo = self.rect.center
            
            # Vira a imagem (flip) se estiver olhando para a esquerda
            if not self.olhando_direita:
                # vira no eixo X (True), não vira no eixo Y (False)
                imagem_nova = pygame.transform.flip(imagem_nova, True, False) 
                
            # Define a nova imagem e atualiza o retângulo
            self.image = imagem_nova
            self.rect = self.image.get_rect()
            
            # Restaura a posição do centro
            self.rect.center = centro_antigo

            
    def pular(self):
        """ Executa a ação de pular. """
        # Só pode pular se NÃO estiver pulando (ou seja, se estiver no chão)
        if not self.pulando:
            self.vel_y = self.forca_pulo
            self.pulando = True

# --- 3. Criação dos Objetos (Antes do Loop) ---

# Cria o nosso personagem! (Chama o __init__ da classe Jogador)
jogador = Jogador() 

# --- 4. Loop Principal do Jogo ---
rodando = True
while rodando:
    # Garante que o jogo rode no máximo a 60 FPS
    clock.tick(FPS) 

    # --- 4a. Processamento de Eventos (Inputs) ---
    for evento in pygame.event.get():
        # Evento: Clicar no "X" de fechar a janela
        if evento.type == pygame.QUIT:
            rodando = False
        
        # Evento: TECLA PRESSIONADA (apenas uma vez)
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE: # Pressionou Espaço
                jogador.pular()
            if evento.key == pygame.K_z: # Pressionou 'Z' (para atirar)
                jogador.atirando = True
                jogador.frame_atual = 0 # Reinicia a animação para o frame 0
                
        # Evento: TECLA SOLTA
        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_z:
                jogador.atirando = False # Para de atirar

    # --- 4b. Checagem de Teclas (para movimento contínuo) ---
    # Isso detecta se a tecla está SENDO SEGURADA
    teclas = pygame.key.get_pressed()
    
    if teclas[pygame.K_LEFT]: # Seta Esquerda
        jogador.vel_x = -5 # Define a velocidade horizontal
        jogador.correndo = True
        jogador.olhando_direita = False # Vira para a esquerda
    elif teclas[pygame.K_RIGHT]: # Seta Direita
        jogador.vel_x = 5
        jogador.correndo = True
        jogador.olhando_direita = True # Vira para a direita
    else:
        # Se não estiver pressionando nem esquerda nem direita
        jogador.vel_x = 0
        jogador.correndo = False

    # --- 4c. Atualização da Lógica ---
    # Chama o método 'update()' do jogador (que roda a gravidade, animar, etc.)
    jogador.update() 

    # --- 4d. Renderização (Desenho) - A ORDEM IMPORTA! ---
    
    # 1. Limpa a tela (preenche com preto)
    tela.fill(PRETO)
    
    # 2. Desenha o jogador na tela
    # Desenha a 'jogador.image' atual na posição 'jogador.rect'
    tela.blit(jogador.image, jogador.rect)
    
    # 3. Atualiza a tela para mostrar o que foi desenhado
    pygame.display.flip()

# --- 5. Finalização ---
# Sai do Pygame quando o loop 'while rodando:' termina
pygame.quit() 