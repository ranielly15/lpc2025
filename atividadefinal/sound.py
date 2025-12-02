import pygame
import os
import random
import time

class SoundManager:
    def __init__(self):
        # Inicializa o mixer
        try:
            # Pre-init é bom para evitar delay no áudio
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            self.sound_enabled = True
        except Exception as e:
            print(f"[Audio] Erro ao iniciar mixer: {e}")
            self.sound_enabled = False
            return

        # ==============================================================================
        # CONFIGURAÇÃO DE VOLUMES (0.0 a 1.0)
        # ==============================================================================
        self.vol_music       = 0.3   # Volume da Trilha Sonora (Fundo)
        
        self.vol_player_bark = 0.6   # Latido do jogador
        self.vol_player_hurt = 0.8   # Som de dano
        self.vol_hiss        = 0.5   # Gato sibilando
        self.vol_npc_bark    = 0.2   # Cães inimigos 
        self.vol_npc_meow    = 0.1   # Gatos miando (ambiente)
        # ==============================================================================

        # --- CORREÇÃO DE CAMINHO ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sound_dir = os.path.join(base_dir, "assets", "sounds")

        print(f"[Audio Debug] Sistema de som iniciado. Pasta: {self.sound_dir}")

        # --- NOMES DOS ARQUIVOS ---
        # Certifique-se que o arquivo existe e a extensão (.mp3 ou .wav) está correta
        self.music_file       = "soundtrack.mp3" 
        
        self.player_bark_file = "caramelBark.mp3"
        self.player_hurt_file = "caramelHurt.mp3"
        self.hiss_file        = "catHiss.mp3"
        
        self.npc_bark_filenames = ["dobermannBark.mp3"] 
        self.npc_meow_filenames = ["blackcatMeow.mp3", "orangecatMeow.mp3"]

        # --- CARREGAMENTO DE EFEITOS SONOROS (SFX) ---
        self.player_bark_sound = self.load_sound(self.player_bark_file, self.vol_player_bark)
        self.player_hurt_sound = self.load_sound(self.player_hurt_file, self.vol_player_hurt)
        self.hiss_sound        = self.load_sound(self.hiss_file, self.vol_hiss)

        self.npc_barks = []
        self.npc_meows = []

        for name in self.npc_bark_filenames:
            snd = self.load_sound(name, self.vol_npc_bark)
            if snd: self.npc_barks.append(snd)

        for name in self.npc_meow_filenames:
            snd = self.load_sound(name, self.vol_npc_meow)
            if snd: self.npc_meows.append(snd)

        # --- INICIA A MÚSICA DE FUNDO ---
        self.play_background_music()

        # --- TIMERS ---
        self.last_bark_time = time.time()
        self.last_meow_time = time.time()
        
        self.BARK_INTERVAL = 5.0
        self.MEOW_INTERVAL = 5.0

    def load_sound(self, filename, volume=1.0):
        """Carrega efeitos sonoros curtos (SFX)."""
        if not self.sound_enabled:
            return None
        
        full_path = os.path.join(self.sound_dir, filename)

        if os.path.exists(full_path):
            try:
                sound = pygame.mixer.Sound(full_path)
                sound.set_volume(volume)
                return sound
            except Exception as e:
                print(f"[Audio] Erro ao carregar SFX {filename}: {e}")
                return None
        else:
            print(f"[Audio] Arquivo SFX NÃO encontrado: {filename}")
            return None

    def play_background_music(self):
        """Carrega e toca a música de fundo em loop (Stream)."""
        if not self.sound_enabled:
            return

        full_path = os.path.join(self.sound_dir, self.music_file)

        if os.path.exists(full_path):
            try:
                # Carrega a música (streaming, não ocupa muita RAM)
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.set_volume(self.vol_music)
                # Toca em loop infinito (-1)
                pygame.mixer.music.play(-1)
                print(f"[Audio] Tocando música: {self.music_file}")
            except Exception as e:
                print(f"[Audio] Erro ao tocar música {self.music_file}: {e}")
        else:
            print(f"[Audio] Arquivo de Música NÃO encontrado: {full_path}")

    def update(self):
        """Chamado a cada frame no Game loop para checar os timers automáticos"""
        if not self.sound_enabled:
            return

        current_time = time.time()

        if current_time - self.last_bark_time >= self.BARK_INTERVAL:
            self.play_random_npc_bark()
            self.last_bark_time = current_time

        if current_time - self.last_meow_time >= self.MEOW_INTERVAL:
            self.play_random_npc_meow()
            self.last_meow_time = current_time

    # --- MÉTODOS DE DISPARO ---

    def play_player_bark(self):
        if self.player_bark_sound:
            self.player_bark_sound.play()

    def play_hurt(self):
        if self.player_hurt_sound:
            self.player_hurt_sound.play()

    def play_hiss(self):
        if self.hiss_sound:
            self.hiss_sound.play()

    def play_random_npc_bark(self):
        if self.npc_barks:
            sound = random.choice(self.npc_barks)
            sound.play()

    def play_random_npc_meow(self):
        if self.npc_meows:
            sound = random.choice(self.npc_meows)
            sound.play()