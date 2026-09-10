"""
MediaDownloader - Portable Open-Source Media Downloader
Copyright (c) 2026 Dunny_616
Licensed under the MIT License.
"""

import sys
import os
import ctypes
import shutil
import urllib.request
import zipfile
import json
import threading
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog
import yt_dlp

try:
    myappid = "MediaDownloader.App.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

def obtener_ruta_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def obtener_ruta_recurso(nombre_archivo):
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', obtener_ruta_base())
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, nombre_archivo)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class MediaDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MediaDownloader")
        self.geometry("520x520")
        self.resizable(False, False)
        self.configure(fg_color="#0b0f19")

        ruta_icono = obtener_ruta_recurso("icon.ico")
        if os.path.exists(ruta_icono):
            try:
                self.iconbitmap(ruta_icono)
            except Exception:
                pass

        self.ruta_destino = os.path.join(os.path.expanduser("~"), "Downloads")

        ruta_recursos = obtener_ruta_recurso("")
        ruta_base = obtener_ruta_base()

        if os.path.exists(os.path.join(ruta_recursos, "ffmpeg.exe")):
            self.dir_ffmpeg = ruta_recursos
        else:
            self.dir_ffmpeg = ruta_base

        os.environ["PATH"] += os.path.pathsep + self.dir_ffmpeg

        COLOR_CARD = "#111827"
        COLOR_BORDE = "#1f2937"
        COLOR_ACCENT = "#a855f7"
        COLOR_ACCENT_HOVER = "#9333ea"
        COLOR_ENTRADA = "#030712"
        COLOR_TEXTO_MUTED = "#9ca3af"

        self.card_main = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=COLOR_CARD,
            border_width=1,
            border_color=COLOR_BORDE
        )
        self.card_main.pack(padx=20, pady=20, fill="both", expand=True)

        self.lbl_header = ctk.CTkLabel(
            self.card_main,
            text="MediaDownloader",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#f3f4f6"
        )
        self.lbl_header.pack(pady=(22, 2))

        self.lbl_sub = ctk.CTkLabel(
            self.card_main,
            text="Descargar videos y música",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXTO_MUTED
        )
        self.lbl_sub.pack(pady=(0, 15))

        self.txt_url = ctk.CTkEntry(
            self.card_main,
            placeholder_text="Pega el enlace aquí...",
            width=440,
            height=44,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDE,
            fg_color=COLOR_ENTRADA,
            text_color="#ffffff",
            placeholder_text_color="#4b5563",
            font=ctk.CTkFont(size=13)
        )
        self.txt_url.pack(pady=8)

        self.opt_formato = ctk.CTkOptionMenu(
            self.card_main,
            values=[
                "🎬 Video - 1080p (Full HD)",
                "🎬 Video - 720p (HD)",
                "🎬 Video - 480p",
                "🎬 Video - 360p",
                "🎧 Audio - MP3 (128 kbps)"
            ],
            width=440,
            height=42,
            corner_radius=10,
            fg_color=COLOR_ENTRADA,
            button_color=COLOR_BORDE,
            button_hover_color=COLOR_ACCENT_HOVER,
            dropdown_fg_color=COLOR_CARD,
            dropdown_hover_color=COLOR_ACCENT_HOVER,
            text_color="#e5e7eb",
            font=ctk.CTkFont(size=13)
        )
        self.opt_formato.pack(pady=8)

        self.btn_descargar = ctk.CTkButton(
            self.card_main,
            text="⬇️  Descargar",
            width=440,
            height=46,
            corner_radius=10,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.iniciar_proceso_hilo
        )
        self.btn_descargar.pack(pady=14)

        self.lbl_estado = ctk.CTkLabel(
            self.card_main,
            text="Listo para descargar",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXTO_MUTED
        )
        self.lbl_estado.pack(pady=(0, 4))

        self.progress = ctk.CTkProgressBar(
            self.card_main,
            width=440,
            height=6,
            corner_radius=3,
            border_width=0,
            progress_color=COLOR_ACCENT,
            fg_color=COLOR_ENTRADA
        )
        self.progress.pack(pady=(0, 18))
        self.progress.set(0)

        self.frame_actions = ctk.CTkFrame(self.card_main, fg_color="transparent")
        self.frame_actions.pack(fill="x", padx=16, pady=(0, 15))

        self.btn_cambiar_ruta = ctk.CTkButton(
            self.frame_actions,
            text="📁  Cambiar ubicación de descargas",
            width=245,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDE,
            fg_color=COLOR_ENTRADA,
            hover_color=COLOR_BORDE,
            text_color="#d1d5db",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.seleccionar_carpeta
        )
        self.btn_cambiar_ruta.pack(side="left", padx=(0, 4))

        self.btn_abrir_carpeta = ctk.CTkButton(
            self.frame_actions,
            text="🔍  Abrir descargas",
            width=190,
            height=38,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_BORDE,
            fg_color=COLOR_ENTRADA,
            hover_color=COLOR_BORDE,
            text_color="#d1d5db",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.abrir_carpeta_descargas
        )
        self.btn_abrir_carpeta.pack(side="right", padx=(4, 0))

    def seleccionar_carpeta(self):
        nueva_carpeta = filedialog.askdirectory(initialdir=self.ruta_destino)
        if nueva_carpeta:
            self.ruta_destino = nueva_carpeta
            messagebox.showinfo("Ubicación actualizada", f"Las descargas se guardarán en:\n{self.ruta_destino}")

    def abrir_carpeta_descargas(self):
        os.makedirs(self.ruta_destino, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(self.ruta_destino)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", self.ruta_destino])
        else:
            subprocess.Popen(["xdg-open", self.ruta_destino])

    def hook_progreso(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').strip()
            p_clean = "".join(c for c in p if c.isdigit() or c == '.')
            try:
                val = float(p_clean) / 100
                self.progress.set(val)
                self.lbl_estado.configure(text=f"Descargando: {p}")
            except ValueError:
                pass
        elif d['status'] == 'finished':
            self.lbl_estado.configure(text="Procesando / Convirtiendo...")

    def descargar_archivo_con_progreso(self, url, destino):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as respuesta, open(destino, 'wb') as out_file:
            total_length = respuesta.getheader('content-length')
            if total_length is None:
                out_file.write(respuesta.read())
            else:
                dl = 0
                total_length = int(total_length)
                block_size = 8192
                while True:
                    buffer = respuesta.read(block_size)
                    if not buffer:
                        break
                    dl += len(buffer)
                    out_file.write(buffer)
                    porcentaje = dl / total_length
                    self.progress.set(porcentaje)
                    self.lbl_estado.configure(text=f"⚙️ Descargando FFmpeg... ({int(porcentaje*100)}%)")

    def obtener_url_latest_ffmpeg(self):
        """Consulta la API de GitHub para obtener la URL directa del archivo zip win64-gpl más reciente."""
        api_url = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"
        req = urllib.request.Request(api_url, headers={
            'User-Agent': 'MediaDownloader-App',
            'Accept': 'application/vnd.github.v3+json'
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                for asset in data.get('assets', []):
                    nombre = asset.get('name', '')
                    if 'win64-gpl' in nombre and nombre.endswith('.zip') and 'shared' not in nombre:
                        return asset.get('browser_download_url')
        except Exception as e:
            print(f"Error consultando API de GitHub: {e}")


        return "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

    def asegurar_ffmpeg(self):
        """Verifica e instala FFmpeg automáticamente consultando el release más reciente de GitHub."""
        ffmpeg_exe = os.path.join(self.dir_ffmpeg, "ffmpeg.exe")
        ffprobe_exe = os.path.join(self.dir_ffmpeg, "ffprobe.exe")

        if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
            return True

        self.lbl_estado.configure(text="⚙️ Consultando última versión de FFmpeg...")
        
        url_ffmpeg = self.obtener_url_latest_ffmpeg()
        zip_temp = os.path.join(self.dir_ffmpeg, "ffmpeg_auto.zip")
        dir_temp = os.path.join(self.dir_ffmpeg, "ffmpeg_auto_temp")

        try:
            self.lbl_estado.configure(text="⚙️ Descargando FFmpeg automáticamente...")
            self.descargar_archivo_con_progreso(url_ffmpeg, zip_temp)
            
            self.lbl_estado.configure(text="⚙️ Extrayendo componentes...")
            with zipfile.ZipFile(zip_temp, 'r') as zip_ref:
                zip_ref.extractall(dir_temp)

            for root, _, files in os.walk(dir_temp):
                for file in files:
                    if file.lower() in ["ffmpeg.exe", "ffprobe.exe"]:
                        shutil.move(os.path.join(root, file), os.path.join(self.dir_ffmpeg, file))

            self.progress.set(0)
            return True
        except Exception as e:
            self.lbl_estado.configure(text="❌ Error con FFmpeg")
            messagebox.showerror(
                "Error de descarga",
                f"No se pudo descargar FFmpeg automáticamente:\n{e}\n\n"
                "Verifica tu conexión a internet o coloca ffmpeg.exe manualmente en la carpeta."
            )
            return False
        finally:
            if os.path.exists(zip_temp):
                os.remove(zip_temp)
            if os.path.exists(dir_temp):
                shutil.rmtree(dir_temp, ignore_errors=True)

    def iniciar_proceso_hilo(self):
        url = self.txt_url.get().strip()
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            messagebox.showwarning("Enlace inválido", "Por favor ingresa un enlace válido.")
            return

        self.btn_descargar.configure(state="disabled")
        self.progress.set(0)

        threading.Thread(target=self.ejecutar_preparacion_y_descarga, args=(url,), daemon=True).start()

    def ejecutar_preparacion_y_descarga(self, url):
        if not self.asegurar_ffmpeg():
            self.btn_descargar.configure(state="normal")
            return

        self.lbl_estado.configure(text="🔍 Analizando enlace...")
        self.analizar_y_descargar(url)

    def analizar_y_descargar(self, url):
        seleccion = self.opt_formato.get()

        if "MP3" in seleccion:
            self.proceder_descarga(url, modo="mp3")
            return

        res_deseada = 1080
        if "720p" in seleccion: res_deseada = 720
        elif "480p" in seleccion: res_deseada = 480
        elif "360p" in seleccion: res_deseada = 360

        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': 'in_playlist'}) as ydl:
                info = ydl.extract_info(url, download=False)

            resoluciones_disponibles = set()
            formatos_origen = info['formats'] if 'formats' in info else info.get('entries', [{}])[0].get('formats', [])

            for f in formatos_origen:
                h = f.get('height')
                vcodec = f.get('vcodec')
                if h and vcodec and vcodec != 'none':
                    resoluciones_disponibles.add(h)

            resoluciones_ordenadas = sorted(list(resoluciones_disponibles), reverse=True)

            if res_deseada in resoluciones_ordenadas:
                res_final = res_deseada
            elif any(r >= res_deseada for r in resoluciones_ordenadas):
                res_final = min([r for r in resoluciones_ordenadas if r >= res_deseada])
            else:
                max_disponible = resoluciones_ordenadas[0] if resoluciones_ordenadas else 360
                respuesta = messagebox.askyesno(
                    "Resolución no disponible",
                    f"El video no cuenta con la calidad {res_deseada}p.\n\n"
                    f"La máxima resolución disponible es {max_disponible}p.\n\n"
                    f"¿Deseas descargarlo en {max_disponible}p?"
                )
                if respuesta:
                    res_final = max_disponible
                else:
                    self.lbl_estado.configure(text="Descarga cancelada.")
                    self.btn_descargar.configure(state="normal")
                    return

            self.proceder_descarga(url, modo="video", res_altura=res_final)

        except Exception as e:
            self.lbl_estado.configure(text="❌ Error de lectura")
            messagebox.showerror("Error", f"No se pudo analizar el enlace:\n{e}")
            self.btn_descargar.configure(state="normal")

    def proceder_descarga(self, url, modo, res_altura=None):
        dir_temp = os.path.join(self.ruta_destino, "_temp_dl")
        os.makedirs(dir_temp, exist_ok=True)

        es_playlist = 'playlist' in url
        plantilla_nombre = '%(playlist_title,s)/%(playlist_index)s - %(title)s.%(ext)s' if es_playlist else '%(title)s.%(ext)s'

        opciones = {
            'outtmpl': {
                'default': os.path.join(self.ruta_destino, plantilla_nombre),
                'temp': os.path.join(dir_temp, '%(title)s.%(ext)s')
            },
            'progress_hooks': [self.hook_progreso],
            'ignoreerrors': True,
            'ffmpeg_location': self.dir_ffmpeg,
            'keepvideo': False,
            'quiet': True,
        }

        if modo == "mp3":
            opciones.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }],
            })
        else:
            opciones.update({
                'format': f'bestvideo[height={res_altura}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height={res_altura}]+bestaudio/best[height={res_altura}]/best',
                'merge_output_format': 'mp4',
            })

        try:
            self.lbl_estado.configure(text="Descargando...")
            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])

            self.progress.set(1)
            self.lbl_estado.configure(text="✅ Descarga completada")
            messagebox.showinfo("Éxito", "Descarga finalizada correctamente.")
        except Exception as e:
            self.lbl_estado.configure(text="❌ Error en descarga")
            messagebox.showerror("Error", f"Ocurrió un problema:\n{e}")
        finally:
            if os.path.exists(dir_temp):
                shutil.rmtree(dir_temp, ignore_errors=True)
            self.btn_descargar.configure(state="normal")

if __name__ == "__main__":
    app = MediaDownloader()
    app.mainloop()