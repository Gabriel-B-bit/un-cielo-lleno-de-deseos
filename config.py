"""Configuración general de «Un cielo lleno de deseos».

Todas las rutas son relativas a la carpeta del proyecto, así que el programa
funciona igual sin importar desde dónde se ejecute.
"""
from pathlib import Path

# --- Rutas -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FUENTES_DIR = ASSETS_DIR / "fuentes"
DATA_DIR = BASE_DIR / "data"

RUTA_PAISAJE = ASSETS_DIR / "paisaje.png"
RUTA_PRINCESA = ASSETS_DIR / "princesa.png"
RUTA_MUSICA = ASSETS_DIR / "musica.mp3"
RUTA_DESEOS = DATA_DIR / "deseos.json"

# --- Ventana ---------------------------------------------------------------
TITULO = "Un cielo lleno de deseos"
ANCHO, ALTO = 1280, 768          # misma proporción que paisaje.png (1280 x 769)
FPS = 60

# --- Escenario (coordenadas sobre la imagen de 1280 x 768) -------------------
Y_ORILLA = 506                   # donde termina la tierra y empieza el lago
Y_PIES = 510                     # línea por la que camina la princesa
LUNA_CENTRO = (316, 140)
LUNA_REFLEJO = (316, 702)

# Contorno aproximado de árboles y montañas: las estrellas solo nacen por encima.
HORIZONTE = [
    (0, 168), (372, 168), (384, 258), (450, 234), (530, 250), (700, 338),
    (850, 380), (960, 344), (1050, 318), (1130, 296), (1280, 346),
]

# --- Paleta ----------------------------------------------------------------
TEXTO = (255, 240, 250)
TEXTO_SUAVE = (214, 186, 226)
ROSA = (255, 150, 200)
CELESTE = (140, 205, 255)
ORO = (255, 222, 140)
PANEL = (26, 12, 50, 218)

# --- Princesa --------------------------------------------------------------
ESCALA_PRINCESA = 2            # cada píxel del sprite se dibuja de 4 x 4
VEL_CAMINAR = 5.0               # píxeles por segundo
LIMITE_IZQ, LIMITE_DER = 170, 1110

# --- Deseos ----------------------------------------------------------------
MAX_CARACTERES_DESEO = 160

# --- Mensajes de las estrellas ---------------------------------------------
# (tipo, texto). Tipos: "motivacion" (azul) y "romantico" (rosa).
# Puedes añadir, quitar o cambiar frases libremente.
MENSAJES = [
    ("motivacion", "Nunca dudes de lo capaz que eres."),
    ("motivacion", "Incluso los días difíciles tienen algo que enseñarnos."),
    ("motivacion", "Sigue adelante, tienes muchas cosas bonitas por descubrir."),
    ("motivacion", "No olvides lo mucho que vales."),
    ("motivacion", "Cada paso, aunque sea pequeño, te acerca a lo que sueñas."),
    ("motivacion", "Respira hondo: lo estás haciendo mejor de lo que crees."),
    ("motivacion", "Eres más fuerte que cualquier día difícil."),
    ("motivacion", "Lo que hoy parece imposible, mañana será tu mejor historia."),
    ("romantico", "Si pudiera pedir un deseo, sería verte sonreír."),
    ("romantico", "Hay personas que hacen especial hasta el momento más sencillo."),
    ("romantico", "Ojalá nunca olvides lo maravillosa que eres."),
    ("romantico", "Algunas personas son como las estrellas: hacen más bonita la oscuridad."),
    ("romantico", "Contigo, hasta el silencio se siente bonito."),
    ("romantico", "Tu sonrisa merece su propia constelación."),
    ("romantico", "Si el cielo guardara recuerdos, estaría lleno de ti."),
    ("romantico", "Esta noche cada estrella brilla un poquito por ti."),
]
