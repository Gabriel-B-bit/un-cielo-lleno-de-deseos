"""La princesa: sprites pixel art generados por código + comportamiento.

* generar_hoja() dibuja los fotogramas con rectángulos de 1 píxel y los guarda
  en assets/princesa.png (una tira horizontal de 10 fotogramas).
* Princesa se encarga de cargar esa tira, animarla y moverla por la orilla.
"""
import math
import random

import pygame

from config import (ESCALA_PRINCESA, LIMITE_DER, LIMITE_IZQ, RUTA_PRINCESA,
                    VEL_CAMINAR, Y_PIES)

# --------------------------------------------------------------------------
#  Hoja de sprites
# --------------------------------------------------------------------------
GW, GH = 24, 36                  # rejilla de dibujo de cada fotograma
FW, FH = GW + 2, GH + 2          # + 1 px de contorno por lado
N_CAMINAR, N_REPOSO, N_MIRAR = 6, 2, 2
N_FOTOGRAMAS = N_CAMINAR + N_REPOSO + N_MIRAR
IDX_REPOSO = N_CAMINAR
IDX_MIRAR = N_CAMINAR + N_REPOSO

PAL = {
    "contorno": (38, 20, 70),
    "pelo": (34, 22, 62), "pelo_luz": (74, 52, 116),
    "piel": (250, 218, 190), "piel_sombra": (226, 172, 150),
    "rubor": (246, 150, 170), "ojo": (30, 18, 52), "brillo": (255, 255, 255),
    "vestido": (60, 112, 224), "luz": (112, 168, 252), "sombra": (38, 74, 170),
    "lazo": (255, 168, 208), "oro": (255, 218, 112), "zapato": (96, 54, 128),
}


def _pose(tipo, i):
    """Devuelve los parámetros de animación del fotograma i de una pose."""
    if tipo == "caminar":
        f = i / N_CAMINAR * 2 * math.pi
        return dict(dy=(0, 0, -1, 0, 0, -1)[i], pelo=round(2.2 * math.sin(f - 0.9)) - 1,
                    falda=1, ondas=i, brazo=round(1.6 * math.sin(f)),
                    pie=round(2.6 * math.sin(f)), paso=math.cos(f),
                    mirar=False, manos=False)
    if tipo == "reposo":
        return dict(dy=-i, pelo=-1 - i, falda=0, ondas=i * 2, brazo=0, pie=0,
                    paso=0, mirar=False, manos=True)
    return dict(dy=-i, pelo=-3 - i, falda=0, ondas=i * 2, brazo=0, pie=0,
                paso=0, mirar=True, manos=True)


def _dibujar_fotograma(tipo, i):
    s = pygame.Surface((GW, GH), pygame.SRCALPHA)
    p = _pose(tipo, i)

    def r(x, y, w, h, c):
        s.fill(PAL[c], (x, y, w, h))

    dy, mirar = p["dy"], p["mirar"]
    cx = 12

    # --- cabello largo por detrás (se mece) --------------------------------
    arriba, abajo = 5 + dy, 26 + dy
    for y in range(arriba, abajo):
        t = (y - arriba) / (abajo - arriba)
        off = round(p["pelo"] * t * t * 1.4)
        ancho = 4 if t < 0.55 else (3 if t < 0.88 else 2)
        x0 = 7 + off
        r(x0, y, ancho, 1, "pelo")
        if y % 3 == 0:
            r(x0 + 1, y, 1, 1, "pelo_luz")

    # --- falda con vuelo -------------------------------------------------
    for y in range(20 + dy, 32):
        k = y - (20 + dy)
        medio = 4 + round(k * 0.38)
        corr = -round(p["falda"] * k / 11 * 2.2)            # el vuelo va hacia atrás
        if y >= 29:
            corr += round(math.sin((y + p["ondas"]) * 1.3))
        x0, x1 = cx - medio + corr, cx + medio + corr
        r(x0, y, x1 - x0 + 1, 1, "vestido")
        r(x0, y, 2, 1, "sombra")
        if k > 2 and (k + p["ondas"]) % 4 != 3:
            r(cx - 2 + corr, y, 1, 1, "sombra")
        if k > 3:
            r(cx + 2 + corr, y, 1, 1, "luz")
        if k % 3 == 0:
            r(x1 - 1, y, 2, 1, "luz")
    # volante del dobladillo
    for x in range(cx - 8 - round(p["falda"] * 2.2), cx + 8 - round(p["falda"] * 2.2) + 1):
        if (x + p["ondas"]) % 3 == 0 and 0 <= x < GW:
            s.fill(PAL["luz"], (x, 31, 1, 1))

    # --- zapatos --------------------------------------------------------
    f1 = 11 + p["pie"]
    f2 = 11 - p["pie"]
    elev1 = 1 if p["paso"] > 0.35 else 0
    elev2 = 1 if p["paso"] < -0.35 else 0
    r(f1, 32 - elev1, 3, 2, "zapato")
    r(f2, 32 - elev2, 3, 2, "zapato")

    # --- torso ------------------------------------------------------------
    r(9, 13 + dy, 7, 7, "vestido")
    r(9, 13 + dy, 2, 7, "sombra")
    r(13, 14 + dy, 1, 5, "luz")
    r(9, 19 + dy, 7, 1, "lazo")                     # cinta de la cintura
    # lazo trasero que se mece con el viento
    lz = p["pelo"] // 2
    r(7 + lz, 19 + dy, 2, 1, "lazo")
    r(6 + lz, 20 + dy, 2, 3, "lazo")
    r(8 + lz, 20 + dy, 1, 2, "lazo")

    # --- cuello y cabeza --------------------------------------------------
    cab = dy - (1 if mirar else 0)                  # al mirar arriba la cabeza se eleva
    r(11, 12 + dy, 3, 2 + (1 if mirar else 0), "piel_sombra")
    r(10, 6 + cab, 6, 6, "piel")                    # cara
    r(11, 12 + cab, 4, 1, "piel")                   # barbilla
    r(16, 9 + cab, 1, 1, "piel")                    # naricilla
    # flequillo y cabello superior
    r(10, 3 + cab, 5, 1, "pelo")
    r(9, 4 + cab, 7, 1, "pelo")
    r(8, 5 + cab, 8, 2, "pelo")
    r(8, 7 + cab, 3, 5, "pelo")                     # mechón lateral
    r(15, 6 + cab, 2, 1, "pelo")                    # flequillo que cae
    r(11, 4 + cab, 2, 1, "pelo_luz")
    # diadema dorada
    r(11, 3 + cab, 3, 1, "oro")
    r(12, 2 + cab, 1, 1, "oro")
    # ojos y mejillas
    ey = 8 if mirar else 9
    r(12, ey + cab, 1, 2, "ojo")
    r(15, ey + cab, 1, 2, "ojo")
    if mirar:
        r(12, ey + cab, 1, 1, "brillo")
    r(11, 11 + cab, 1, 1, "rubor")
    r(15, 11 + cab, 1, 1, "rubor")
    r(14, 12 + cab, 1, 1, "piel_sombra")            # sonrisa

    # --- brazos -----------------------------------------------------------
    if p["manos"]:
        yh = 15 + dy if mirar else 17 + dy          # manos junto al pecho al mirar el cielo
        r(11, 14 + dy, 3, yh - 14 - dy + 1, "luz")
        r(11, yh + 1, 3, 2, "piel")
    else:
        bx = 11 + p["brazo"]
        r(bx, 14 + dy, 2, 6, "luz")
        r(bx, 20 + dy, 2, 2, "piel")
    return s


def _con_contorno(s):
    """Añade un contorno oscuro de 1 píxel alrededor de las formas opacas."""
    out = pygame.Surface((s.get_width() + 2, s.get_height() + 2), pygame.SRCALPHA)
    out.blit(s, (1, 1))
    w, h = out.get_size()
    base = out.copy()
    for y in range(h):
        for x in range(w):
            if base.get_at((x, y)).a:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and base.get_at((nx, ny)).a:
                    out.set_at((x, y), PAL["contorno"])
                    break
    return out


def generar_hoja(ruta=RUTA_PRINCESA):
    """Dibuja todos los fotogramas y los guarda en una tira PNG."""
    hoja = pygame.Surface((FW * N_FOTOGRAMAS, FH), pygame.SRCALPHA)
    k = 0
    for tipo, n in (("caminar", N_CAMINAR), ("reposo", N_REPOSO), ("mirar", N_MIRAR)):
        for i in range(n):
            hoja.blit(_con_contorno(_dibujar_fotograma(tipo, i)), (k * FW, 0))
            k += 1
    ruta.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(hoja, str(ruta))
    return hoja


def _cargar_hoja():
    if RUTA_PRINCESA.is_file():
        try:
            hoja = pygame.image.load(str(RUTA_PRINCESA)).convert_alpha()
            if hoja.get_size() == (FW * N_FOTOGRAMAS, FH):
                return hoja
        except pygame.error:
            pass
    return generar_hoja().convert_alpha()    # si falta el PNG se regenera solo


# --------------------------------------------------------------------------
#  Comportamiento
# --------------------------------------------------------------------------
class Princesa:
    ACEL = 38.0                      # px/s² -> arranca y frena con suavidad

    def __init__(self):
        hoja = _cargar_hoja()
        e = ESCALA_PRINCESA
        crudos = [hoja.subsurface((i * FW, 0, FW, FH)).copy() for i in range(N_FOTOGRAMAS)]
        self.der = [pygame.transform.scale(f, (FW * e, FH * e)) for f in crudos]
        self.izq = [pygame.transform.flip(f, True, False) for f in self.der]
        caja = self.der[0].get_bounding_rect()
        self.base = caja.bottom                      # fila donde apoyan los pies
        self.reflejos = {False: self._crear_reflejos(self.der),
                         True: self._crear_reflejos(self.izq)}

        self.x = 300.0
        self.dir = 1                 # sentido de la marcha
        self.cara = 1                # hacia dónde mira el sprite
        self.vel = 0.0
        self.estado = "caminar"      # "caminar" | "pausa"
        self.t_anim = 0.0
        self.hasta_pausa = random.uniform(5, 9)
        self.t_pausa = 0.0
        self.t_quieta = 0.0
        self.quiere_mirar = False
        self.retardo_mirar = 0.5
        self.girar_al_acabar = False
        self.mirando = False

    # ---- reflejo en el lago (precalculado) --------------------------------
    @staticmethod
    def _crear_reflejos(frames):
        res = []
        for f in frames:
            r = pygame.transform.flip(f, False, True)
            h = r.get_height()
            for y in range(h):                       # se desvanece hacia abajo
                a = int(120 * (1 - y / h) ** 1.4)
                r.fill((190, 150, 235, a), (0, y, r.get_width(), 1),
                       special_flags=pygame.BLEND_RGBA_MULT)
            res.append(r)
        return res

    # ---- reacciones --------------------------------------------------------
    def mirar_estrella(self, x_estrella):
        """Se detiene y levanta la mirada hacia una estrella fugaz."""
        self.quiere_mirar = True
        self.retardo_mirar = 0.3
        self.hasta_pausa = random.uniform(9, 15)
        if self.estado == "caminar":
            self.estado = "pausa"
            self.t_pausa = 3.0
            self.t_quieta = 0.0
            self.girar_al_acabar = False
        else:
            self.t_pausa = max(self.t_pausa, 2.6)
        self._cara_hacia = 1 if x_estrella > self.x else -1

    def _iniciar_pausa(self, mirar, duracion, girar=False):
        self.estado = "pausa"
        self.t_pausa = duracion
        self.t_quieta = 0.0
        self.quiere_mirar = mirar
        self.retardo_mirar = 0.5
        self.girar_al_acabar = girar
        self._cara_hacia = None

    # ---- actualización -----------------------------------------------------
    def actualizar(self, dt):
        objetivo = VEL_CAMINAR if self.estado == "caminar" else 0.0
        paso = self.ACEL * dt
        self.vel += max(-paso, min(paso, objetivo - self.vel))
        self.x += self.dir * self.vel * dt

        if self.estado == "caminar":
            self.cara = self.dir
            self.t_anim += dt * 4.5 * (self.vel / VEL_CAMINAR)
            self.hasta_pausa -= dt
            if self.x <= LIMITE_IZQ or self.x >= LIMITE_DER:
                self.x = max(LIMITE_IZQ, min(LIMITE_DER, self.x))
                self._iniciar_pausa(False, 1.4, girar=True)
            elif self.hasta_pausa <= 0:
                self._iniciar_pausa(True, random.uniform(4.0, 6.5))
            self.mirando = False
        else:
            if self.vel < 1.0:                       # ya está quieta
                self.vel = 0.0
                self.t_quieta += dt
                self.t_anim += dt
                if getattr(self, "_cara_hacia", None):
                    self.cara = self._cara_hacia
                self.mirando = self.quiere_mirar and self.t_quieta > self.retardo_mirar
                self.t_pausa -= dt
                if self.t_pausa <= 0:
                    if self.girar_al_acabar:
                        self.dir = -self.dir
                    self.cara = self.dir
                    self.estado = "caminar"
                    self.mirando = False
                    self.quiere_mirar = False
                    self.hasta_pausa = random.uniform(9, 16)
            else:
                self.t_anim += dt * 6.5 * (self.vel / VEL_CAMINAR)

    # ---- dibujo ------------------------------------------------------------
    def _indice(self):
        if self.estado == "caminar" or self.vel > 6:
            return int(self.t_anim) % N_CAMINAR
        if self.mirando:
            return IDX_MIRAR + int(self.t_anim * 0.9) % N_MIRAR
        return IDX_REPOSO + int(self.t_anim * 1.1) % N_REPOSO

    def _origen(self, ancho):
        return int(self.x - ancho / 2), Y_PIES - self.base

    def dibujar(self, pantalla):
        frames = self.der if self.cara > 0 else self.izq
        img = frames[self._indice()]
        x, y = self._origen(img.get_width())
        sombra = pygame.Surface((70, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (20, 4, 30, 90), sombra.get_rect())
        pantalla.blit(sombra, (int(self.x - 35), Y_PIES - 8))
        pantalla.blit(img, (x, y))

    def dibujar_reflejo(self, pantalla, t):
        img = self.reflejos[self.cara < 0][self._indice()]
        x, _ = self._origen(img.get_width())
        h, w = img.get_height(), img.get_width()
        arriba = h - self.base              # filas vacías sobre los pies reflejados
        y_ini = Y_PIES + 2
        for y in range(arriba, h, 3):       # cada franja de 3 px ondula un poco
            dx = int(round(2.5 * math.sin(t * 2.0 + y * 0.22)))
            pantalla.blit(img, (x + dx, y_ini + y - arriba), area=(0, y, w, 3))


if __name__ == "__main__":
    # python princesa.py  -> vuelve a dibujar assets/princesa.png
    pygame.init()
    generar_hoja()
    print(f"Sprites regenerados en {RUTA_PRINCESA}")
