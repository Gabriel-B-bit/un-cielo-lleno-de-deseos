"""Almacenamiento de los deseos en data/deseos.json.

Formato del archivo:
    {"version": 1, "deseos": [
        {"id": "a1b2c3d4", "texto": "...", "x": 640, "y": 120,
         "fecha": "2026-11-08T21:30:00"}
    ]}
"""
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

VERSION = 1


class AlmacenDeseos:
    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self.deseos = []
        self.aviso = None            # texto de error legible, si algo falló
        existia = self.ruta.is_file()
        self.cargar()
        if not existia:
            self.guardar()           # crea data/deseos.json vacío la primera vez

    # ------------------------------------------------------------------ carga
    def cargar(self):
        self.deseos = []
        if not self.ruta.is_file():
            return
        try:
            with open(self.ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            crudos = datos.get("deseos", []) if isinstance(datos, dict) else datos
            validos = (self._validar(d) for d in crudos)
            self.deseos = [d for d in validos if d]
        except (OSError, ValueError, TypeError, AttributeError):
            # Archivo ilegible o dañado: se conserva una copia y se empieza limpio
            self._respaldar_corrupto()

    def _respaldar_corrupto(self):
        copia = self.ruta.with_name(f"deseos.corrupto-{int(time.time())}.json")
        try:
            os.replace(self.ruta, copia)
            self.aviso = f"deseos.json estaba dañado; copia guardada como {copia.name}"
        except OSError:
            self.aviso = "No se pudo leer deseos.json"

    @staticmethod
    def _validar(d):
        if not isinstance(d, dict):
            return None
        texto = str(d.get("texto", "")).strip()
        try:
            x, y = float(d["x"]), float(d["y"])
        except (KeyError, TypeError, ValueError):
            return None
        if not texto:
            return None
        return {
            "id": str(d.get("id") or uuid.uuid4().hex[:8]),
            "texto": texto,
            "x": x,
            "y": y,
            "fecha": str(d.get("fecha") or datetime.now().isoformat(timespec="seconds")),
        }

    # --------------------------------------------------------------- guardado
    def guardar(self):
        """Escribe el JSON de forma atómica. Devuelve True si todo salió bien."""
        try:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            temporal = self.ruta.with_name(self.ruta.name + ".tmp")
            with open(temporal, "w", encoding="utf-8") as f:
                json.dump({"version": VERSION, "deseos": self.deseos}, f,
                          ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporal, self.ruta)   # reemplazo atómico: nunca queda a medias
            return True
        except OSError as e:
            self.aviso = f"No se pudo escribir deseos.json ({e.strerror or e})"
            return False

    def agregar(self, texto, x, y):
        """Añade un deseo y lo guarda. Devuelve (deseo, guardado_ok)."""
        deseo = {
            "id": uuid.uuid4().hex[:8],
            "texto": " ".join(texto.split()),
            "x": round(float(x), 1),
            "y": round(float(y), 1),
            "fecha": datetime.now().isoformat(timespec="seconds"),
        }
        self.deseos.append(deseo)
        return deseo, self.guardar()
