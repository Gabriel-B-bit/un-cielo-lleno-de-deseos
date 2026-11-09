"""Música ambiental con pygame.mixer.music (no bloquea el bucle principal)."""
import pygame


class Reproductor:
    def __init__(self, ruta, volumen=0.5):
        self.ruta = ruta
        self.volumen = max(0.0, min(1.0, volumen))
        self.disponible = False
        self.pausado = False
        self.error = None
        self._iniciar()

    def _iniciar(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except pygame.error:
                self.error = "No hay dispositivo de audio disponible"
                return
        if not self.ruta.is_file():
            self.error = f"Falta la canción: {self.ruta.parent.name}/{self.ruta.name}"
            return
        try:
            pygame.mixer.music.load(str(self.ruta))
            pygame.mixer.music.set_volume(self.volumen)
            pygame.mixer.music.play(loops=-1, fade_ms=2500)   # bucle infinito
            self.disponible = True
        except pygame.error:
            self.error = "No se pudo reproducir musica.mp3 (¿es un MP3 válido?)"

    def alternar(self):
        if not self.disponible:
            return
        if self.pausado:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.pausado = not self.pausado

    def cambiar_volumen(self, volumen):
        self.volumen = max(0.0, min(1.0, volumen))
        if self.disponible:
            pygame.mixer.music.set_volume(self.volumen)

    def detener(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
