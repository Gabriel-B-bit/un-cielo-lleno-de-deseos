"""Un cielo lleno de deseos — un pequeño universo digital hecho con Pygame.

Ejecutar:  python main.py
"""
import sys

import pygame

from almacenamiento import AlmacenDeseos
from audio import Reproductor
from config import (ALTO, ANCHO, FPS, RUTA_DESEOS, RUTA_MUSICA, RUTA_PAISAJE, TITULO)
from escenario import Cielo, Lago
from interfaz import (Aviso, BarraControles, BolsaMensajes, DialogoDeseo, Fuentes,
                      GestorMensajes, PanelDeseos, fecha_legible, icono_ventana)
from princesa import Princesa


class Aplicacion:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITULO)
        pygame.display.set_icon(icono_ventana())
        banderas = pygame.SCALED | pygame.RESIZABLE        # se adapta a cualquier pantalla
        try:
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO), banderas, vsync=1)
        except pygame.error:
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO), banderas)
        self.reloj = pygame.time.Clock()
        self.fondo = self._cargar_fondo()

        # --- datos y sonido ---
        self.almacen = AlmacenDeseos(RUTA_DESEOS)
        self.musica = Reproductor(RUTA_MUSICA, volumen=0.5)

        # --- mundo ---
        self.lago = Lago(self.fondo)
        self.cielo = Cielo(self.almacen.deseos)
        self.princesa = Princesa()

        # --- interfaz ---
        fuentes = Fuentes()
        self.barra = BarraControles(fuentes)
        self.mensajes = GestorMensajes(fuentes)
        self.aviso = Aviso(fuentes)
        self.dialogo = DialogoDeseo(fuentes)
        self.panel = PanelDeseos(fuentes)
        self.bolsa = BolsaMensajes()

        self.fugaz_capturada = None
        self.t = 0.0
        self.corriendo = True
        self._cursor_mano = False
        self._preparar_avisos()

    # ------------------------------------------------------------------ inicio
    @staticmethod
    def _cargar_fondo():
        try:
            img = pygame.image.load(str(RUTA_PAISAJE)).convert()
        except (pygame.error, FileNotFoundError):
            print(f"No se encontró el paisaje: {RUTA_PAISAJE}\n"
                  "Copia paisaje.png dentro de la carpeta assets.")
            pygame.quit()
            sys.exit(1)
        if img.get_size() != (ANCHO, ALTO):
            img = pygame.transform.smoothscale(img, (ANCHO, ALTO))
        return img

    def _preparar_avisos(self):
        if self.almacen.aviso:
            self.aviso.programar(1.0, self.almacen.aviso, 6.0)
        if not self.musica.disponible:
            if not RUTA_MUSICA.is_file():
                self.aviso.programar(1.5, "Para tener música, copia musica.mp3 en la carpeta assets", 6.0)
            else:
                self.aviso.programar(1.5, self.musica.error, 6.0)
        self.aviso.programar(8.0, "Toca las estrellas  ·  Atrapa una fugaz para pedir un deseo", 9.0)

    # ------------------------------------------------------------------ eventos
    def _procesar_evento(self, e):
        if e.type == pygame.QUIT:
            self.corriendo = False
            return
        if e.type == pygame.MOUSEBUTTONUP:
            self.barra.arrastrando = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
            return

        if self.dialogo.activo:                                  # ventana modal
            r = self.dialogo.manejar_evento(e)
            if r:
                self._resolver_dialogo(r)
            return
        if self.panel.activo:                                    # lista de deseos
            r = self.panel.manejar_evento(e, self.almacen.deseos)
            if r and r[0] == "cerrar":
                self.panel.cerrar()
            elif r and r[0] == "ir":
                self._ir_a_deseo(r[1])
            return

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                self.musica.alternar()
            elif e.key == pygame.K_UP:
                self.musica.cambiar_volumen(self.musica.volumen + 0.05)
            elif e.key == pygame.K_DOWN:
                self.musica.cambiar_volumen(self.musica.volumen - 0.05)
            return
        accion = self.barra.manejar_evento(e)
        if accion:
            self._accion_barra(accion)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self._clic_en_cielo(e.pos)

    def _accion_barra(self, accion):
        if accion[0] == "musica":
            if self.musica.disponible:
                self.musica.alternar()
            else:
                self.aviso.mostrar(self.musica.error or "Sin música", 4.0)
        elif accion[0] == "volumen":
            self.musica.cambiar_volumen(accion[1])
        elif accion[0] == "deseos":
            self.panel.abrir()
        elif accion[0] == "salir":
            self.corriendo = False

    def _clic_en_cielo(self, pos):
        objetivo = self.cielo.objetivo_en(pos)
        if not objetivo:
            return
        tipo, obj = objetivo
        if tipo == "estrella":
            kind, texto = self.bolsa.siguiente()
            obj.flash = 1.0
            self.mensajes.mostrar(texto, (obj.x, obj.y), kind)
        elif tipo == "deseo":
            self.mensajes.mostrar(obj.texto, (obj.x, obj.y), "deseo",
                                  titulo="Tu deseo", pie=fecha_legible(obj.fecha))
        elif tipo == "fugaz":
            obj.capturar()
            self.fugaz_capturada = obj
            self.cielo.pausa_fugaces = True
            self.dialogo.abrir()

    def _resolver_dialogo(self, resultado):
        fugaz = self.fugaz_capturada
        self.dialogo.cerrar()
        self.cielo.pausa_fugaces = False
        self.fugaz_capturada = None
        if resultado[0] == "guardar" and fugaz:
            x, y = self.cielo.ajustar_posicion(fugaz.x, fugaz.y)
            deseo, guardado = self.almacen.agregar(resultado[1], x, y)
            self.cielo.agregar_deseo(deseo, nueva=True)
            fugaz.viva = False                        # la estrella fugaz se vuelve estrella fija
            if guardado:
                self.aviso.mostrar("Tu deseo ahora brilla en el cielo", 4.5)
            else:
                self.aviso.mostrar(self.almacen.aviso or "No se pudo guardar el deseo", 7.0)
        elif fugaz:
            fugaz.liberar()

    def _ir_a_deseo(self, deseo):
        self.panel.cerrar()
        est = self.cielo.destacar(deseo["id"])
        if est:
            self.mensajes.mostrar(est.texto, (est.x, est.y), "deseo",
                                  titulo="Tu deseo", pie=fecha_legible(est.fecha))

    # -------------------------------------------------------------- actualización
    def _actualizar(self, dt):
        self.t += dt
        self.lago.actualizar(dt)
        self.cielo.actualizar(dt)
        for f in self.cielo.nuevas:                   # una fugaz nueva: la princesa la mira
            self.princesa.mirar_estrella(f.x)
        self.cielo.nuevas.clear()
        self.princesa.actualizar(dt)
        self.mensajes.actualizar(dt)
        self.aviso.actualizar(dt)

    # -------------------------------------------------------------------- dibujo
    def _dibujar(self):
        p, t = self.pantalla, self.t
        pos = pygame.mouse.get_pos()
        modal = self.dialogo.activo or self.panel.activo
        pos_ui = (-1000, -1000) if modal else pos      # sin resaltados bajo una ventana modal

        p.blit(self.fondo, (0, 0))
        self.lago.dibujar(p, t)
        self.princesa.dibujar_reflejo(p, t)
        hover = self.cielo.dibujar(p, t, None if modal else pos)
        self.princesa.dibujar(p)
        self.mensajes.dibujar(p)
        self.aviso.dibujar(p)
        self.barra.dibujar(p, self.musica, len(self.almacen.deseos), pos_ui)
        if self.panel.activo:
            self.panel.dibujar(p, self.almacen.deseos, pos)
        if self.dialogo.activo:
            self.dialogo.dibujar(p, self._dt, pos)

        if self.dialogo.activo:
            mano = self.dialogo.bajo_cursor(pos)
        elif self.panel.activo:
            mano = self.panel.bajo_cursor(pos, self.almacen.deseos)
        else:
            mano = self.barra.bajo_cursor(pos) or hover is not None
        self._poner_cursor(mano)

    def _poner_cursor(self, mano):
        if mano != self._cursor_mano:
            self._cursor_mano = mano
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if mano else pygame.SYSTEM_CURSOR_ARROW)

    # ------------------------------------------------------------------ bucle
    def ejecutar(self):
        self._dt = 0.0
        while self.corriendo:
            self._dt = min(self.reloj.tick(FPS) / 1000.0, 0.05)   # delta time en segundos
            for e in pygame.event.get():
                self._procesar_evento(e)
            self._actualizar(self._dt)
            self._dibujar()
            pygame.display.flip()
        self.musica.detener()
        pygame.quit()


def main():
    Aplicacion().ejecutar()


if __name__ == "__main__":
    main()
