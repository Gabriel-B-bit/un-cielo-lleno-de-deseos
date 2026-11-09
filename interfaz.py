"""Interfaz: fuentes, iconos, mensajes, controles, diálogo de deseos y lista."""
import random
from datetime import datetime

import pygame

from config import (ALTO, ANCHO, CELESTE, FUENTES_DIR, MAX_CARACTERES_DESEO,
                    MENSAJES, ORO, PANEL, ROSA, TEXTO, TEXTO_SUAVE)

# --------------------------------------------------------------------------
#  Utilidades de dibujo
# --------------------------------------------------------------------------
class Fuentes:
    """Fuentes pixeladas de assets/fuentes (con alternativa si faltan)."""

    def __init__(self):
        pygame.font.init()
        self.titulo = self._cargar("PressStart2P-Regular.ttf", 16)
        self.texto = self._cargar("VT323-Regular.ttf", 30)
        self.pequena = self._cargar("VT323-Regular.ttf", 24)

    @staticmethod
    def _cargar(nombre, tam):
        candidatas = [FUENTES_DIR / nombre] + sorted(FUENTES_DIR.glob("*.ttf"))
        for ruta in candidatas:
            try:
                return pygame.font.Font(str(ruta), tam)
            except (OSError, pygame.error):
                continue
        return pygame.font.SysFont("consolas,couriernew,monospace", tam)


def render(fuente, texto, color):
    return fuente.render(texto, False, color)       # sin suavizado = píxeles nítidos


def ajustar_texto(fuente, texto, ancho):
    """Divide el texto en líneas que caben en `ancho` píxeles."""
    lineas, actual = [], ""
    for palabra in texto.split(" "):
        prueba = palabra if not actual else actual + " " + palabra
        if fuente.size(prueba)[0] <= ancho or not actual:
            actual = prueba
            while fuente.size(actual)[0] > ancho and len(actual) > 1:
                k = len(actual)
                while k > 1 and fuente.size(actual[:k])[0] > ancho:
                    k -= 1
                lineas.append(actual[:k])
                actual = actual[k:]
        else:
            lineas.append(actual)
            actual = palabra
    lineas.append(actual)
    return lineas


def recortar(fuente, texto, ancho):
    if fuente.size(texto)[0] <= ancho:
        return texto
    while texto and fuente.size(texto + "...")[0] > ancho:
        texto = texto[:-1]
    return texto + "..."


def panel_pixel(ancho, alto, relleno=PANEL, borde=ROSA, esq=4):
    """Panel con esquinas escalonadas y borde de 2 px."""
    s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.rect(s, borde, (esq, 0, ancho - 2 * esq, alto))
    pygame.draw.rect(s, borde, (0, esq, ancho, alto - 2 * esq))
    pygame.draw.rect(s, borde, (2, 2, ancho - 4, alto - 4))
    b = 2
    pygame.draw.rect(s, relleno, (esq, b, ancho - 2 * esq, alto - 2 * b))
    pygame.draw.rect(s, relleno, (b, esq, ancho - 2 * b, alto - 2 * esq))
    pygame.draw.rect(s, relleno, (esq - 1, b + 1, ancho - 2 * esq + 2, alto - 2 * b - 2))
    pygame.draw.rect(s, relleno, (b + 1, esq - 1, ancho - 2 * b - 2, alto - 2 * esq + 2))
    return s


BITMAPS = {
    "pausa": ["........", ".##..##.", ".##..##.", ".##..##.", ".##..##.", ".##..##.",
              ".##..##.", "........"],
    "play": ["..#.....", "..##....", "..###...", "..####..", "..####..", "..###...",
             "..##....", "..#....."],
    "estrella": ["...#...", "...#...", "#######", ".#####.", "..###..", ".##.##.",
                 ".#...#."],
    "cerrar": ["##....##", ".##..##.", "..####..", "...##...", "..####..", ".##..##.",
               "##....##"],
    "nota": ["...####.", "...#..#.", "...#..#.", "...#..#.", ".###.##.", ".###.##.",
             "........"],
}
_cache_iconos = {}


def icono(nombre, color, escala=2):
    clave = (nombre, color, escala)
    if clave not in _cache_iconos:
        filas = BITMAPS[nombre]
        s = pygame.Surface((len(filas[0]) * escala, len(filas) * escala), pygame.SRCALPHA)
        for y, fila in enumerate(filas):
            for x, c in enumerate(fila):
                if c == "#":
                    s.fill(color, (x * escala, y * escala, escala, escala))
        _cache_iconos[clave] = s
    return _cache_iconos[clave]


def icono_ventana():
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    s.fill((40, 14, 80), (0, 0, 32, 32))
    s.blit(icono("estrella", ORO, 4), (2, 2))
    return s


def fecha_legible(iso):
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    try:
        d = datetime.fromisoformat(iso)
        return f"{d.day} {meses[d.month - 1]} {d.year}"
    except ValueError:
        return ""


def _boton(texto, fuente, rect, activo, hover, color):
    borde = color if (hover and activo) else (TEXTO_SUAVE if activo else (110, 90, 130))
    relleno = (70, 30, 100, 235) if (hover and activo) else (36, 16, 64, 235)
    surf = panel_pixel(rect.w, rect.h, relleno, borde)
    img = render(fuente, texto, TEXTO if activo else (140, 120, 160))
    surf.blit(img, img.get_rect(center=(rect.w // 2, rect.h // 2 - 2)))
    return surf


# --------------------------------------------------------------------------
#  Mensajes flotantes y avisos
# --------------------------------------------------------------------------
class BolsaMensajes:
    """Reparte las frases sin repetir hasta haberlas visto todas."""

    def __init__(self):
        self.pendientes = []
        self.ultimo = None

    def siguiente(self):
        if not self.pendientes:
            self.pendientes = MENSAJES[:]
            random.shuffle(self.pendientes)
            if self.ultimo in self.pendientes[-1:]:
                self.pendientes.reverse()
        self.ultimo = self.pendientes.pop()
        return self.ultimo


ACENTOS = {"motivacion": CELESTE, "romantico": ROSA, "deseo": ORO}


class Mensaje:
    APARECER, DESAPARECER = 0.55, 1.0

    def __init__(self, fuentes, texto, pos, tipo, titulo=None, pie=None):
        acento = ACENTOS[tipo]
        lineas = ajustar_texto(fuentes.texto, texto, 520)
        imgs = [render(fuentes.texto, l, TEXTO) for l in lineas]
        cab = render(fuentes.titulo, titulo, acento) if titulo else None
        pie_img = render(fuentes.pequena, pie, TEXTO_SUAVE) if pie else None
        cuerpo_w = max([i.get_width() for i in imgs] + [cab.get_width() if cab else 0,
                                                        pie_img.get_width() if pie_img else 0])
        alto_lin = fuentes.texto.get_linesize() - 4
        h = 30 + (cab.get_height() + 12 if cab else 0) + alto_lin * len(imgs) \
            + (pie_img.get_height() + 6 if pie_img else 0)
        w = cuerpo_w + 44
        self.surf = pygame.Surface((w, h + 12), pygame.SRCALPHA)
        self.surf.blit(panel_pixel(w, h, (24, 10, 48, 226), acento), (0, 12))
        # insignia con una estrellita sobre el borde superior
        pygame.draw.rect(self.surf, (24, 10, 48), (w // 2 - 16, 10, 32, 8))
        ic = icono("estrella", acento, 3)
        self.surf.blit(ic, (w // 2 - ic.get_width() // 2, 0))
        y = 12 + 18
        if cab:
            self.surf.blit(cab, (w // 2 - cab.get_width() // 2, y))
            y += cab.get_height() + 12
        for im in imgs:
            self.surf.blit(im, (w // 2 - im.get_width() // 2, y))
            y += alto_lin
        if pie_img:
            self.surf.blit(pie_img, (w // 2 - pie_img.get_width() // 2, y + 4))
        # posición: centrada sobre la estrella (o debajo si no cabe arriba)
        x = max(16, min(ANCHO - 16 - w, pos[0] - w // 2))
        y = pos[1] - h - 36
        if y < 70:
            y = pos[1] + 26
        self.pos = (int(x), int(y))
        self.t = 0.0
        self.total = self.APARECER + 3.6 + 0.045 * len(texto) + self.DESAPARECER

    def acortar(self):
        self.t = max(self.t, self.total - 0.35)

    @property
    def viva(self):
        return self.t < self.total

    def dibujar(self, pantalla):
        if self.t < self.APARECER:
            k = self.t / self.APARECER
            a = 1 - (1 - k) ** 3
        elif self.t > self.total - self.DESAPARECER:
            a = max(0.0, (self.total - self.t) / self.DESAPARECER)
        else:
            a = 1.0
        self.surf.set_alpha(int(255 * a))
        pantalla.blit(self.surf, (self.pos[0], self.pos[1] + int((1 - a) * 10)))


class GestorMensajes:
    def __init__(self, fuentes):
        self.fuentes = fuentes
        self.mensajes = []

    def mostrar(self, texto, pos, tipo, titulo=None, pie=None):
        for m in self.mensajes:
            m.acortar()
        self.mensajes.append(Mensaje(self.fuentes, texto, pos, tipo, titulo, pie))

    def actualizar(self, dt):
        for m in self.mensajes:
            m.t += dt
        self.mensajes = [m for m in self.mensajes if m.viva]

    def dibujar(self, pantalla):
        for m in self.mensajes:
            m.dibujar(pantalla)


class Aviso:
    """Texto discreto en la parte baja (pistas y errores)."""

    def __init__(self, fuentes):
        self.fuentes = fuentes
        self.surf = None
        self.t = self.total = 0.0
        self.cola = []              # avisos programados: [segundos_de_espera, texto, dur, color]

    def programar(self, espera, texto, dur=6.0, color=TEXTO_SUAVE):
        self.cola.append([espera, texto, dur, color])

    def mostrar(self, texto, dur=4.5, color=TEXTO):
        img = render(self.fuentes.texto, texto, color)
        w, h = img.get_width() + 36, img.get_height() + 12
        self.surf = panel_pixel(w, h, (20, 8, 40, 200), (150, 100, 180))
        self.surf.blit(img, (18, 4))
        self.t, self.total = 0.0, dur

    def actualizar(self, dt):
        for item in self.cola[:]:
            item[0] -= dt
            if item[0] <= 0:
                self.cola.remove(item)
                self.mostrar(item[1], item[2], item[3])
        self.t += dt

    def dibujar(self, pantalla):
        if not self.surf or self.t >= self.total:
            return
        a = min(1.0, self.t / 0.6, (self.total - self.t) / 0.8)
        self.surf.set_alpha(int(255 * max(0.0, a)))
        pantalla.blit(self.surf, self.surf.get_rect(midbottom=(ANCHO // 2, ALTO - 18)))


# --------------------------------------------------------------------------
#  Controles (arriba a la derecha)
# --------------------------------------------------------------------------
class BarraControles:
    def __init__(self, fuentes):
        self.f = fuentes
        y, s = 16, 36
        x = ANCHO - 16 - (s + 8 + 104 + 8 + s + 8 + s)
        self.r_musica = pygame.Rect(x, y, s, s)
        self.r_vol = pygame.Rect(x + s + 8, y, 104, s)
        self.r_deseos = pygame.Rect(self.r_vol.right + 8, y, s, s)
        self.r_cerrar = pygame.Rect(self.r_deseos.right + 8, y, s, s)
        self.arrastrando = False

    def _volumen_en(self, x):
        return max(0.0, min(1.0, (x - (self.r_vol.x + 8)) / (self.r_vol.w - 16)))

    def bajo_cursor(self, pos):
        return any(r.collidepoint(pos) for r in
                   (self.r_musica, self.r_vol, self.r_deseos, self.r_cerrar))

    def manejar_evento(self, e):
        """Devuelve ('musica',) ('volumen', v) ('deseos',) ('salir',) o None."""
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.r_musica.collidepoint(e.pos):
                return ("musica",)
            if self.r_vol.collidepoint(e.pos):
                self.arrastrando = True
                return ("volumen", self._volumen_en(e.pos[0]))
            if self.r_deseos.collidepoint(e.pos):
                return ("deseos",)
            if self.r_cerrar.collidepoint(e.pos):
                return ("salir",)
        elif e.type == pygame.MOUSEMOTION and self.arrastrando:
            return ("volumen", self._volumen_en(e.pos[0]))
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.arrastrando = False
        return None

    def dibujar(self, pantalla, reproductor, n_deseos, pos):
        f = self.f
        # --- música ---
        hov = self.r_musica.collidepoint(pos)
        pantalla.blit(_boton("", f.pequena, self.r_musica, reproductor.disponible, hov, ROSA),
                      self.r_musica)
        if reproductor.disponible:
            nombre = "play" if reproductor.pausado else "pausa"
            col = ROSA if hov else TEXTO
        else:
            nombre, col = "nota", (120, 100, 140)
        ic = icono(nombre, col, 2)
        pantalla.blit(ic, ic.get_rect(center=self.r_musica.center))
        # --- volumen ---
        hv = self.r_vol.collidepoint(pos) or self.arrastrando
        pantalla.blit(_boton("", f.pequena, self.r_vol, True, hv, ROSA), self.r_vol)
        pista = pygame.Rect(self.r_vol.x + 10, self.r_vol.centery - 3, self.r_vol.w - 20, 6)
        pygame.draw.rect(pantalla, (90, 60, 120), pista)
        lleno = pista.copy()
        lleno.w = int(pista.w * reproductor.volumen)
        pygame.draw.rect(pantalla, ROSA, lleno)
        perilla = pygame.Rect(0, 0, 8, 18)
        perilla.center = (pista.x + lleno.w, pista.centery)
        pygame.draw.rect(pantalla, TEXTO, perilla)
        # --- deseos ---
        hd = self.r_deseos.collidepoint(pos)
        pantalla.blit(_boton("", f.pequena, self.r_deseos, True, hd, ORO), self.r_deseos)
        ic = icono("estrella", ORO if hd else TEXTO, 3)
        pantalla.blit(ic, ic.get_rect(center=self.r_deseos.center))
        if n_deseos:
            n = render(f.pequena, str(n_deseos), ORO)
            pantalla.blit(n, n.get_rect(bottomright=(self.r_deseos.right - 3, self.r_deseos.bottom + 3)))
        # --- cerrar ---
        hc = self.r_cerrar.collidepoint(pos)
        pantalla.blit(_boton("", f.pequena, self.r_cerrar, True, hc, ROSA), self.r_cerrar)
        ic = icono("cerrar", ROSA if hc else TEXTO, 2)
        pantalla.blit(ic, ic.get_rect(center=self.r_cerrar.center))
        # --- pista emergente ---
        tip = None
        if hov:
            tip = ("Pausar música" if not reproductor.pausado else "Reanudar música") \
                if reproductor.disponible else (reproductor.error or "Sin música")
        elif hv:
            tip = f"Volumen {int(reproductor.volumen * 100)}%"
        elif hd:
            tip = "Mis deseos"
        elif hc:
            tip = "Salir"
        if tip:
            img = render(f.pequena, tip, TEXTO)
            fondo = panel_pixel(img.get_width() + 20, img.get_height() + 8, (20, 8, 40, 235),
                                (150, 100, 180))
            fondo.blit(img, (10, 2))
            x = min(ANCHO - 12 - fondo.get_width(), pos[0] - fondo.get_width() // 2)
            pantalla.blit(fondo, (x, self.r_musica.bottom + 8))


# --------------------------------------------------------------------------
#  Ventana para escribir un deseo
# --------------------------------------------------------------------------
class DialogoDeseo:
    def __init__(self, fuentes):
        self.f = fuentes
        self.activo = False
        self.texto = ""
        self.t = 0.0
        self.rect = pygame.Rect(0, 0, 720, 372)
        self.rect.center = (ANCHO // 2, ALTO // 2 - 30)
        r = self.rect
        self.caja = pygame.Rect(r.x + 30, r.y + 118, r.w - 60, 150)
        self.r_guardar = pygame.Rect(r.right - 30 - 190, r.bottom - 30 - 44, 190, 44)
        self.r_cancelar = pygame.Rect(self.r_guardar.x - 14 - 190, self.r_guardar.y, 190, 44)
        self.fondo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.fondo.fill((12, 4, 30, 130))
        self.panel = panel_pixel(r.w, r.h, (26, 12, 52, 245), ORO, 6)

    def abrir(self):
        self.activo, self.texto, self.t = True, "", 0.0
        pygame.key.start_text_input()
        pygame.key.set_repeat(380, 35)

    def cerrar(self):
        self.activo = False
        pygame.key.stop_text_input()
        pygame.key.set_repeat(0)

    @property
    def puede_guardar(self):
        return bool(self.texto.strip())

    def bajo_cursor(self, pos):
        return (self.r_guardar.collidepoint(pos) and self.puede_guardar) \
            or self.r_cancelar.collidepoint(pos)

    def manejar_evento(self, e):
        """Devuelve ('guardar', texto), ('cancelar',) o None."""
        if e.type == pygame.TEXTINPUT:
            limpio = "".join(c for c in e.text if c.isprintable())
            if len(self.texto) + len(limpio) <= MAX_CARACTERES_DESEO:
                self.texto += limpio
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                return ("cancelar",)
            if e.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.puede_guardar:
                return ("guardar", self.texto.strip())
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.r_guardar.collidepoint(e.pos) and self.puede_guardar:
                return ("guardar", self.texto.strip())
            if self.r_cancelar.collidepoint(e.pos):
                return ("cancelar",)
        return None

    def dibujar(self, pantalla, dt, pos):
        self.t += dt
        pantalla.blit(self.fondo, (0, 0))
        pantalla.blit(self.panel, self.rect)
        r, f = self.rect, self.f
        tit = render(f.titulo, "Pide un deseo", ORO)
        pantalla.blit(tit, tit.get_rect(midtop=(r.centerx, r.y + 26)))
        sub = render(f.texto, "Escríbelo aquí y se convertirá en una estrella.", TEXTO_SUAVE)
        pantalla.blit(sub, sub.get_rect(midtop=(r.centerx, r.y + 68)))
        # caja de texto
        pygame.draw.rect(pantalla, (14, 6, 30), self.caja)
        pygame.draw.rect(pantalla, (150, 100, 180), self.caja, 2)
        lineas = ajustar_texto(f.texto, self.texto, self.caja.w - 28)
        alto = f.texto.get_linesize() - 4
        for i, l in enumerate(lineas[:5]):
            pantalla.blit(render(f.texto, l, TEXTO), (self.caja.x + 14, self.caja.y + 10 + i * alto))
        if int(self.t * 2) % 2 == 0:                        # cursor parpadeante
            ultima = lineas[min(len(lineas), 5) - 1]
            cx = self.caja.x + 14 + f.texto.size(ultima)[0] + 2
            cy = self.caja.y + 12 + (min(len(lineas), 5) - 1) * alto
            pygame.draw.rect(pantalla, ROSA, (cx, cy, 3, f.texto.get_height() - 12))
        cont = render(f.pequena, f"{len(self.texto)}/{MAX_CARACTERES_DESEO}", TEXTO_SUAVE)
        pantalla.blit(cont, cont.get_rect(topright=(self.caja.right, self.caja.bottom + 4)))
        pantalla.blit(_boton("Cancelar", f.texto, self.r_cancelar, True,
                             self.r_cancelar.collidepoint(pos), ROSA), self.r_cancelar)
        pantalla.blit(_boton("Guardar", f.texto, self.r_guardar, self.puede_guardar,
                             self.r_guardar.collidepoint(pos), ORO), self.r_guardar)


# --------------------------------------------------------------------------
#  Lista de deseos guardados
# --------------------------------------------------------------------------
class PanelDeseos:
    ALTO_ITEM = 92

    def __init__(self, fuentes):
        self.f = fuentes
        self.activo = False
        self.scroll = 0.0
        self.rect = pygame.Rect(0, 0, 740, 560)
        self.rect.center = (ANCHO // 2, ALTO // 2)
        r = self.rect
        self.lista = pygame.Rect(r.x + 26, r.y + 92, r.w - 52, r.h - 92 - 26)
        self.r_cerrar = pygame.Rect(r.right - 18 - 36, r.y + 18, 36, 36)
        self.fondo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        self.fondo.fill((12, 4, 30, 130))
        self.panel = panel_pixel(r.w, r.h, (26, 12, 52, 245), ROSA, 6)
        self._cache = {}

    def abrir(self):
        self.activo, self.scroll = True, 0.0

    def cerrar(self):
        self.activo = False

    def _items(self, deseos):
        return list(reversed(deseos))              # los más recientes primero

    def _max_scroll(self, n):
        return max(0.0, n * self.ALTO_ITEM - self.lista.h)

    def _lineas(self, d):
        if d["id"] not in self._cache:
            lin = ajustar_texto(self.f.texto, d["texto"], self.lista.w - 60)
            if len(lin) > 2:
                lin = [lin[0], recortar(self.f.texto, lin[1] + " " + " ".join(lin[2:]),
                                        self.lista.w - 60)]
            self._cache[d["id"]] = lin
        return self._cache[d["id"]]

    def _item_en(self, pos, deseos):
        if not self.lista.collidepoint(pos):
            return None
        i = int((pos[1] - self.lista.y + self.scroll) // self.ALTO_ITEM)
        items = self._items(deseos)
        return items[i] if 0 <= i < len(items) else None

    def bajo_cursor(self, pos, deseos):
        return self.r_cerrar.collidepoint(pos) or self._item_en(pos, deseos) is not None

    def manejar_evento(self, e, deseos):
        """Devuelve ('ir', deseo), ('cerrar',) o None."""
        n = len(deseos)
        if e.type == pygame.MOUSEWHEEL:
            self.scroll = max(0.0, min(self._max_scroll(n), self.scroll - e.y * 56))
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return ("cerrar",)
            if e.key in (pygame.K_DOWN, pygame.K_UP):
                paso = 56 if e.key == pygame.K_DOWN else -56
                self.scroll = max(0.0, min(self._max_scroll(n), self.scroll + paso))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.r_cerrar.collidepoint(e.pos) or not self.rect.collidepoint(e.pos):
                return ("cerrar",)
            d = self._item_en(e.pos, deseos)
            if d:
                return ("ir", d)
        return None

    def dibujar(self, pantalla, deseos, pos):
        f, r = self.f, self.rect
        pantalla.blit(self.fondo, (0, 0))
        pantalla.blit(self.panel, r)
        tit = render(f.titulo, "Mis deseos", ROSA)
        pantalla.blit(tit, (r.x + 30, r.y + 28))
        hc = self.r_cerrar.collidepoint(pos)
        pantalla.blit(_boton("", f.pequena, self.r_cerrar, True, hc, ROSA), self.r_cerrar)
        ic = icono("cerrar", ROSA if hc else TEXTO, 2)
        pantalla.blit(ic, ic.get_rect(center=self.r_cerrar.center))

        items = self._items(deseos)
        if not items:
            for i, l in enumerate(("Aún no has pedido ningún deseo.",
                                   "Atrapa una estrella fugaz y escribe el primero.")):
                img = render(f.texto, l, TEXTO_SUAVE)
                pantalla.blit(img, img.get_rect(center=(r.centerx, r.centery + i * 34)))
            return
        sub = render(f.pequena, f"{len(items)} deseo{'s' if len(items) != 1 else ''} · toca uno para verlo en el cielo",
                     TEXTO_SUAVE)
        pantalla.blit(sub, (r.x + 30, r.y + 62))
        self.scroll = min(self.scroll, self._max_scroll(len(items)))
        pantalla.set_clip(self.lista)
        sobre = self._item_en(pos, deseos)
        for i, d in enumerate(items):
            y = self.lista.y + i * self.ALTO_ITEM - int(self.scroll)
            if y > self.lista.bottom or y + self.ALTO_ITEM < self.lista.y:
                continue
            caja = pygame.Rect(self.lista.x, y + 4, self.lista.w - 14, self.ALTO_ITEM - 10)
            pygame.draw.rect(pantalla, (70, 32, 104) if d is sobre else (40, 18, 70), caja)
            pygame.draw.rect(pantalla, ORO if d is sobre else (110, 70, 140), caja, 2)
            pantalla.blit(icono("estrella", ORO, 2), (caja.x + 14, caja.y + 12))
            pantalla.blit(render(f.pequena, fecha_legible(d["fecha"]), TEXTO_SUAVE),
                          (caja.x + 40, caja.y + 6))
            for k, l in enumerate(self._lineas(d)):
                pantalla.blit(render(f.texto, l, TEXTO), (caja.x + 16, caja.y + 32 + k * 26))
        pantalla.set_clip(None)
        if self._max_scroll(len(items)) > 0:                 # barra de desplazamiento
            total = len(items) * self.ALTO_ITEM
            h = max(30, int(self.lista.h * self.lista.h / total))
            y = self.lista.y + int((self.lista.h - h) * self.scroll / self._max_scroll(len(items)))
            pygame.draw.rect(pantalla, ROSA, (self.lista.right - 6, y, 6, h))
