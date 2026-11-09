"""Paisaje animado: cielo (estrellas, fugaces, deseos, luna) y lago."""
import math
import random

import pygame

from config import (ALTO, ANCHO, HORIZONTE, LUNA_CENTRO, LUNA_REFLEJO, ORO,
                    Y_ORILLA)


def limite_cielo(x):
    """Altura máxima (y) hasta la que hay cielo despejado en la columna x."""
    pts = HORIZONTE
    x = max(pts[0][0], min(pts[-1][0], x))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * ((x - x0) / (x1 - x0) if x1 > x0 else 0)
    return pts[-1][1]


def crear_brillo(radio, color, intensidad=1.0, potencia=2.0):
    """Círculo luminoso con degradado suave (para halos de luna y estrellas)."""
    s = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
    for r in range(radio, 0, -1):
        a = int(255 * intensidad * (1 - r / radio) ** potencia)
        pygame.draw.circle(s, (*color, a), (radio, radio), r)
    return s


def _rotulo(s, color, x, y, brazo, alpha):
    """Destello de cuatro puntas dibujado píxel a píxel."""
    c = (*color, alpha)
    s.fill(c, (x - 1, y - 1, 2, 2))
    for k in range(1, brazo + 1):
        a = (*color, int(alpha * (1 - k / (brazo + 1))))
        s.fill(a, (x - 1 - k, y, 1, 1))
        s.fill(a, (x + 1 + k - 1, y, 1, 1))
        s.fill(a, (x, y - 1 - k, 1, 1))
        s.fill(a, (x, y + 1 + k - 1, 1, 1))


# --------------------------------------------------------------------------
#  Objetos del cielo
# --------------------------------------------------------------------------
class EstrellaFija:
    """Estrella parpadeante. Al hacer clic muestra un mensaje."""
    RADIO_CLIC = 16

    def __init__(self, x, y, tam, rng):
        self.x, self.y, self.tam = x, y, tam
        self.fase = rng.uniform(0, math.tau)
        self.vel = rng.uniform(0.8, 2.2)
        self.color = rng.choice([(255, 255, 255), (255, 244, 220), (214, 230, 255)])
        self.flash = 0.0                 # destello extra tras un clic

    def actualizar(self, dt):
        self.flash = max(0.0, self.flash - dt * 1.4)

    def dibujar(self, capa, t, hover, brillos):
        b = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * self.vel + self.fase))
        b = min(1.0, b + self.flash)
        a = int(255 * b)
        x, y = int(self.x), int(self.y)
        if self.tam == 1:
            capa.fill((*self.color, a), (x - 1, y - 1, 2, 2))
        elif self.tam == 2:
            _rotulo(capa, self.color, x, y, 2, a)
        else:
            halo = brillos["blanco"]
            halo.set_alpha(int(90 * b))
            capa.blit(halo, (x - halo.get_width() // 2, y - halo.get_height() // 2))
            _rotulo(capa, self.color, x, y, 5, a)
        if self.flash > 0:
            pygame.draw.circle(capa, (255, 255, 255, int(160 * self.flash)),
                               (x, y), int(6 + 18 * (1 - self.flash)), 1)
        if hover:
            pygame.draw.circle(capa, (255, 255, 255, 120), (x, y), 10, 1)


class EstrellaFugaz:
    """Estrella fugaz con estela. Es lo bastante lenta como para atraparla."""
    RADIO_CLIC = 36

    def __init__(self, rng):
        ang = math.radians(rng.uniform(14, 26))
        self.sentido = -1 if rng.random() < 0.7 else 1
        self.dx, self.dy = self.sentido * math.cos(ang), math.sin(ang)
        y0 = rng.uniform(30, 170)
        self.x0 = rng.uniform(640, 1230) if self.sentido < 0 else rng.uniform(60, 600)
        self.y0 = y0
        largo = min(rng.uniform(480, 640), (395 - y0) / math.sin(ang))
        self.duracion = largo / rng.uniform(175, 235)
        self.largo = largo
        self.t = 0.0
        self.x, self.y = self.x0, self.y0
        self.capturada = False
        self.viva = True
        self.pulso = 0.0

    @property
    def envolvente(self):
        p = self.t / self.duracion
        return min(1.0, p / 0.12, (1.0 - p) / 0.25)

    @property
    def clicable(self):
        return self.viva and (self.capturada or self.envolvente > 0.25)

    def capturar(self):
        self.capturada = True

    def liberar(self):
        self.capturada = False

    def actualizar(self, dt):
        self.pulso += dt
        if self.capturada:
            return
        self.t += dt
        p = self.t / self.duracion
        if p >= 1.0:
            self.viva = False
            return
        self.x = self.x0 + self.dx * self.largo * p
        self.y = self.y0 + self.dy * self.largo * p

    def dibujar(self, capa, t, hover, brillos):
        env = 1.0 if self.capturada else max(0.0, self.envolvente)
        if env <= 0:
            return
        # estela: cuadraditos que se desvanecen y encogen
        n, paso = 46, 3.2
        for i in range(n):
            f = i / n
            px = self.x - self.dx * i * paso
            py = self.y - self.dy * i * paso
            lado = 3 if f < 0.25 else (2 if f < 0.6 else 1)
            a = int(255 * env * (1 - f) ** 1.7)
            if a > 3:
                col = (255, 255, 255) if f < 0.3 else (255, 200, 235)
                capa.fill((*col, a), (int(px) - lado // 2, int(py) - lado // 2, lado, lado))
        halo = brillos["rosa"]
        halo.set_alpha(int(200 * env))
        capa.blit(halo, (int(self.x) - halo.get_width() // 2,
                         int(self.y) - halo.get_height() // 2))
        _rotulo(capa, (255, 255, 255), int(self.x), int(self.y), 4, int(255 * env))
        # anillo discreto que invita a hacer clic
        a = int((70 + 40 * math.sin(self.pulso * 5)) * env)
        pygame.draw.circle(capa, (255, 220, 240, a), (int(self.x), int(self.y)),
                           16 + (4 if hover else 0), 1)


class EstrellaDeseo:
    """Estrella dorada que guarda un deseo escrito por el usuario."""
    RADIO_CLIC = 20

    def __init__(self, datos, nueva=False):
        self.id = datos["id"]
        self.texto = datos["texto"]
        self.fecha = datos["fecha"]
        self.x, self.y = datos["x"], datos["y"]
        self.edad = 0.0 if nueva else 99.0
        self.fase = (hash(self.id) % 1000) / 1000 * math.tau
        self.resalte = 0.0

    def actualizar(self, dt):
        self.edad += dt
        self.resalte = max(0.0, self.resalte - dt)

    def dibujar(self, capa, t, hover, brillos):
        nac = min(1.0, self.edad / 1.4)
        esc = 1 - (1 - nac) ** 3 + 0.25 * math.sin(nac * math.pi)   # rebote suave
        pulso = 0.5 + 0.5 * math.sin(t * 1.6 + self.fase)
        x, y = int(self.x), int(self.y)
        halo = brillos["oro"]
        halo.set_alpha(int((110 + 70 * pulso) * min(1.0, nac * 1.5)))
        capa.blit(halo, (x - halo.get_width() // 2, y - halo.get_height() // 2))
        _rotulo(capa, ORO, x, y, max(1, int(8 * esc)), 255)
        capa.fill((255, 255, 255, 255), (x - 1, y - 1, 2, 2))
        if self.edad < 1.8:                                   # onda de nacimiento
            r = int(6 + 60 * (self.edad / 1.8))
            pygame.draw.circle(capa, (255, 230, 170, int(200 * (1 - self.edad / 1.8))),
                               (x, y), r, 2)
        if self.resalte > 0:
            r = int(14 + 10 * math.sin(t * 8))
            pygame.draw.circle(capa, (255, 236, 190, int(255 * min(1, self.resalte))),
                               (x, y), r, 2)
        if hover:
            pygame.draw.circle(capa, (255, 255, 255, 140), (x, y), 14, 1)


# --------------------------------------------------------------------------
#  Cielo
# --------------------------------------------------------------------------
class Cielo:
    ALTO_CAPA = 440

    def __init__(self, deseos_guardados):
        rng = random.Random(7)                  # misma constelación en cada ejecución
        self.rng = random.Random()
        self.capa = pygame.Surface((ANCHO, self.ALTO_CAPA), pygame.SRCALPHA)
        self.brillos = {
            "blanco": crear_brillo(14, (255, 255, 255), 0.55),
            "rosa": crear_brillo(26, (255, 190, 230), 0.8),
            "oro": crear_brillo(30, (255, 214, 120), 0.8),
        }
        self.halo_luna = crear_brillo(96, (225, 205, 255), 0.55)
        self.estrellas = self._crear_estrellas(rng)
        self.fugaces = []
        self.deseos = [EstrellaDeseo(d) for d in deseos_guardados]
        self.particulas = []
        self.hasta_fugaz = 3.5                   # la primera llega pronto
        self.pausa_fugaces = False
        self.nuevas = []                         # fugaces recién creadas (las lee main)

    # ---- creación -----------------------------------------------------------
    def _crear_estrellas(self, rng, n=62):
        lista = []
        intentos = 0
        while len(lista) < n and intentos < 4000:
            intentos += 1
            x = rng.uniform(14, ANCHO - 14)
            tope = limite_cielo(x) - 14
            if tope < 60:
                continue
            y = 16 + (tope - 16) * rng.random() ** 1.15
            if math.hypot(x - LUNA_CENTRO[0], y - LUNA_CENTRO[1]) < 78:
                continue
            if x > 1000 and y < 74:              # zona de los controles
                continue
            if any(math.hypot(x - e.x, y - e.y) < 40 for e in lista):
                continue
            tam = rng.choices([1, 2, 3], [0.55, 0.33, 0.12])[0]
            lista.append(EstrellaFija(x, y, tam, rng))
        return lista

    def ajustar_posicion(self, x, y):
        """Coloca una estrella-deseo dentro del cielo y sin pisar a otra."""
        x = max(40, min(ANCHO - 40, x))
        y = max(40, min(limite_cielo(x) - 20, y))
        if x > 980 and y < 84:
            y = 84
        for _ in range(40):
            if all(math.hypot(x - d.x, y - d.y) > 34 for d in self.deseos):
                break
            x += self.rng.uniform(-30, 30)
            y += self.rng.uniform(-20, 20)
            x = max(40, min(ANCHO - 40, x))
            y = max(40, min(limite_cielo(x) - 20, y))
        return x, y

    def agregar_deseo(self, datos, nueva=True):
        d = EstrellaDeseo(datos, nueva)
        self.deseos.append(d)
        if nueva:
            for _ in range(22):
                ang = self.rng.uniform(0, math.tau)
                vel = self.rng.uniform(30, 120)
                self.particulas.append([d.x, d.y, math.cos(ang) * vel,
                                        math.sin(ang) * vel, self.rng.uniform(0.8, 1.6), 0.0])
        return d

    def destacar(self, id_deseo):
        for d in self.deseos:
            if d.id == id_deseo:
                d.resalte = 3.0
                return d
        return None

    # ---- actualización -----------------------------------------------------
    def actualizar(self, dt):
        for e in self.estrellas:
            e.actualizar(dt)
        for d in self.deseos:
            d.actualizar(dt)
        for f in self.fugaces:
            f.actualizar(dt)
        self.fugaces = [f for f in self.fugaces if f.viva]
        for p in self.particulas:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[2] *= 0.97
            p[3] *= 0.97
            p[5] += dt
        self.particulas = [p for p in self.particulas if p[5] < p[4]]

        if not self.pausa_fugaces:
            self.hasta_fugaz -= dt
            if self.hasta_fugaz <= 0 and len(self.fugaces) < 3:
                f = EstrellaFugaz(self.rng)
                self.fugaces.append(f)
                self.nuevas.append(f)
                self.hasta_fugaz = self.rng.uniform(4.5, 9.5)

    # ---- interacción ---------------------------------------------------------
    def objetivo_en(self, pos):
        """Qué hay bajo el cursor: ('deseo'|'fugaz'|'estrella', objeto) o None."""
        mx, my = pos
        for d in reversed(self.deseos):
            if math.hypot(mx - d.x, my - d.y) <= d.RADIO_CLIC:
                return "deseo", d
        for f in self.fugaces:
            if f.clicable and math.hypot(mx - f.x, my - f.y) <= f.RADIO_CLIC:
                return "fugaz", f
        mejor, dmin = None, EstrellaFija.RADIO_CLIC
        for e in self.estrellas:
            dist = math.hypot(mx - e.x, my - e.y)
            if dist <= dmin:
                mejor, dmin = e, dist
        return ("estrella", mejor) if mejor else None

    # ---- dibujo ----------------------------------------------------------------
    def dibujar(self, pantalla, t, pos_raton):
        # halo de la luna y destellos en sus puntas
        pulso = 0.5 + 0.5 * math.sin(t * 0.9)
        self.halo_luna.set_alpha(int(95 + 55 * pulso))
        pantalla.blit(self.halo_luna, (LUNA_CENTRO[0] - 96 - 6, LUNA_CENTRO[1] - 96 + 4))

        capa = self.capa
        capa.fill((0, 0, 0, 0))
        hover = self.objetivo_en(pos_raton) if pos_raton else None
        sel = hover[1] if hover else None
        for e in self.estrellas:
            e.dibujar(capa, t, e is sel, self.brillos)
        for sx, sy, ph in ((294, 99, 0.0), (355, 162, 2.1)):          # puntas de la luna
            a = 0.5 + 0.5 * math.sin(t * 1.7 + ph)
            _rotulo(capa, (255, 245, 255), sx, sy, 4 + int(3 * a), int(120 + 135 * a))
        for d in self.deseos:
            d.dibujar(capa, t, d is sel, self.brillos)
        for f in self.fugaces:
            f.dibujar(capa, t, f is sel, self.brillos)
        for x, y, vx, vy, vida, edad in self.particulas:
            a = int(255 * (1 - edad / vida))
            capa.fill((255, 226, 160, a), (int(x), int(y), 2, 2))
        pantalla.blit(capa, (0, 0))
        return hover


# --------------------------------------------------------------------------
#  Lago
# --------------------------------------------------------------------------
class Lago:
    FRANJA = 2

    def __init__(self, fondo):
        self.alto = ALTO - Y_ORILLA
        self.fuente = fondo.subsurface((0, Y_ORILLA, ANCHO, self.alto)).copy()
        self.capa = pygame.Surface((ANCHO, self.alto), pygame.SRCALPHA)
        self.rng = random.Random()
        self.ondas = []
        self.hasta_onda = 0.3
        self.brillo_luna = crear_brillo(70, (235, 200, 255), 0.5)
        self.destellos = []
        for i in range(46):
            cerca = i < 14                                      # algunos junto a la luna
            x = self.rng.gauss(LUNA_REFLEJO[0], 55) if cerca else self.rng.uniform(20, ANCHO - 20)
            y = self.rng.gauss(LUNA_REFLEJO[1], 22) if cerca else self.rng.uniform(530, 755)
            self.destellos.append(dict(
                x=x, y=min(max(y, Y_ORILLA + 14), ALTO - 8),
                largo=self.rng.randint(5, 16), fase=self.rng.uniform(0, math.tau),
                vel=self.rng.uniform(0.7, 1.9)))

    def actualizar(self, dt):
        for o in self.ondas:
            o["t"] += dt
        self.ondas = [o for o in self.ondas if o["t"] < o["dur"]]
        self.hasta_onda -= dt
        if self.hasta_onda <= 0:
            y = self.rng.uniform(Y_ORILLA + 28, ALTO - 20)
            prof = (y - Y_ORILLA) / self.alto                  # más cerca = más grande
            self.ondas.append(dict(x=self.rng.uniform(50, ANCHO - 50), y=y,
                                   rmax=8 + 44 * prof + self.rng.uniform(0, 10),
                                   dur=self.rng.uniform(3.2, 4.6), t=0.0))
            self.hasta_onda = self.rng.uniform(0.5, 1.5)

    def dibujar(self, pantalla, t):
        # reflejo: cada franja se desplaza lateralmente con ondas lentas
        for y in range(0, self.alto, self.FRANJA):
            prof = y / self.alto
            amp = 0.5 + 3.2 * prof
            dx = amp * (math.sin(t * 1.15 + y * 0.085) * 0.65 + math.sin(t * 0.6 - y * 0.037) * 0.35)
            pantalla.blit(self.fuente, (int(round(dx)), Y_ORILLA + y),
                          area=(0, y, ANCHO, self.FRANJA))
        capa = self.capa
        capa.fill((0, 0, 0, 0))
        # brillo de la luna sobre el agua
        self.brillo_luna.set_alpha(int(80 + 40 * math.sin(t * 1.1)))
        capa.blit(self.brillo_luna, (LUNA_REFLEJO[0] - 70, LUNA_REFLEJO[1] - 70 - Y_ORILLA))
        # destellos que titilan
        for d in self.destellos:
            b = 0.5 + 0.5 * math.sin(t * d["vel"] + d["fase"])
            a = int(170 * b ** 2)
            if a > 6:
                dx = int(2 * math.sin(t * 0.8 + d["fase"]))
                capa.fill((255, 205, 240, a), (int(d["x"]) + dx, int(d["y"]) - Y_ORILLA,
                                                d["largo"], 1))
        # ondas elípticas que se expanden y se desvanecen
        for o in self.ondas:
            p = o["t"] / o["dur"]
            for k, retraso in enumerate((0.0, 0.22)):
                q = p - retraso
                if q <= 0:
                    continue
                r = o["rmax"] * q / (1 - retraso)
                a = int(150 * (1 - q) ** 1.6)
                if a > 4 and r >= 2:
                    rect = pygame.Rect(0, 0, int(r * 2), max(2, int(r * 0.5)))
                    rect.center = (int(o["x"]), int(o["y"]) - Y_ORILLA)
                    pygame.draw.ellipse(capa, (255, 200, 240, a), rect, 1)
        pantalla.blit(capa, (0, Y_ORILLA))
