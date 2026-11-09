UN CIELO LLENO DE DESEOS
========================
Un pequeño universo digital en pixel art: un lago bajo un cielo estrellado, una
princesa que pasea por la orilla, estrellas con mensajes bonitos y estrellas
fugaces que se convierten en deseos que se quedan guardados.

REQUISITOS
----------
* Windows 11 (también funciona en macOS/Linux)
* Python 3.11  (https://www.python.org/downloads/)
* Pygame (se instala con requirements.txt)


INSTALACIÓN Y EJECUCIÓN EN POWERSHELL (Windows 11)
--------------------------------------------------
1) Abre PowerShell y entra en la carpeta del proyecto:

       cd "C:\ruta\donde\esta\UNIVERSO_PARA_TI"

2) Crea un entorno virtual (solo la primera vez):

       py -3.11 -m venv .venv

3) Instala las dependencias SIN activar el entorno (evita problemas de permisos):

       .\.venv\Scripts\python.exe -m pip install --upgrade pip
       .\.venv\Scripts\python.exe -m pip install -r requirements.txt

4) Ejecuta el proyecto:

       .\.venv\Scripts\python.exe main.py

   (Si prefieres activar el entorno: .\.venv\Scripts\Activate.ps1 y luego
    "python main.py". Si PowerShell bloquea el script, ejecuta antes:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass )

   Si no usas entorno virtual, basta con:
       py -3.11 -m pip install -r requirements.txt
       py -3.11 main.py


CÓMO SE USA
-----------
* Haz clic en cualquier estrella del cielo: aparece un mensaje bonito.
* Cada cierto tiempo cruza una estrella fugaz (la princesa se detiene a mirarla).
  Haz clic sobre ella mientras brilla: se abre una ventana para escribir un deseo.
  - Enter o botón «Guardar»: el deseo se convierte en una estrella dorada.
  - Esc o «Cancelar»: la estrella fugaz sigue su camino.
* Haz clic en una estrella dorada para volver a leer su deseo.
* Botones de arriba a la derecha: pausar/reanudar música, volumen (arrastra la
  barra), lista de deseos (estrella) y cerrar (X).
* Atajos: Espacio = pausar/reanudar música · Flechas arriba/abajo = volumen ·
  F11 = pantalla completa · Esc = cerrar ventanas.


CÓMO AGREGAR O CAMBIAR LA CANCIÓN
---------------------------------
1) Copia tu archivo MP3 dentro de la carpeta  assets  con el nombre exacto:

       assets\musica.mp3

   (para cambiarla, reemplaza ese archivo por otro MP3 con el mismo nombre)
2) Vuelve a abrir el programa. Suena en bucle desde el inicio con un fundido suave.
Si el archivo no existe o no es válido, el programa funciona igual (sin música) y
muestra un aviso discreto. Si quieres otro nombre o ruta, cambia RUTA_MUSICA en
config.py.


CÓMO SE GUARDAN Y RECUPERAN LOS DESEOS
--------------------------------------
* Al pulsar «Guardar», el deseo se escribe de inmediato en  data\deseos.json
  (texto, posición de la estrella en el cielo y fecha).
* La escritura es atómica: primero se crea un archivo temporal y luego reemplaza
  al anterior, así el archivo no queda a medias si el programa se cierra justo
  entonces.
* Al iniciar, el programa lee deseos.json y vuelve a poner cada estrella dorada en
  su sitio. Si el archivo no existe, se crea vacío. Si estuviera dañado, se guarda
  una copia como deseos.corrupto-<número>.json y se empieza limpio.
* Puedes copiar deseos.json para hacer una copia de seguridad, o editarlo con el
  Bloc de notas (cierra antes el programa). Es el único lugar donde se guardan.


ESTRUCTURA
----------
UNIVERSO_PARA_TI/
  main.py            bucle principal, eventos del teclado y ratón
  config.py          rutas, tamaños, paleta y la lista de mensajes de las estrellas
  escenario.py       cielo (estrellas, fugaces, luna, deseos) y lago animado
  princesa.py        sprites pixel art de la princesa + comportamiento
  interfaz.py        mensajes, controles, ventana de deseos y lista
  almacenamiento.py  lectura/escritura de deseos.json
  audio.py           música con pygame.mixer
  requirements.txt
  assets/            paisaje.png, princesa.png, musica.mp3 (la pones tú), fuentes/
  data/              deseos.json


PERSONALIZAR
------------
* Mensajes de las estrellas: edita la lista MENSAJES en config.py.
* Princesa: assets/princesa.png es una tira de 10 fotogramas de 26x38 px
  (6 caminando, 2 en reposo, 2 mirando al cielo). Si la borras, el programa la
  vuelve a dibujar solo; también puedes regenerarla con:
       .\.venv\Scripts\python.exe princesa.py
  Puedes sustituirla por tu propio pixel art respetando ese formato.
* Velocidad y límites de su paseo: VEL_CAMINAR, LIMITE_IZQ, LIMITE_DER en config.py.


NOTAS
-----
* El paisaje es tu imagen, sin modificar; solo se le superponen animaciones.
  Se muestra a 1280 x 768 (la imagen original mide 1280 x 769).
* Si tu pantalla es baja (por ejemplo 1366 x 768), pulsa F11 o redimensiona la
  ventana: el juego se escala manteniendo la proporción.
* Fuentes incluidas: Press Start 2P y VT323 (licencia SIL OFL; ver assets/fuentes).
