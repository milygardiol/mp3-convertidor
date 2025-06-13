import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
#from pytube import YouTube
from moviepy import AudioFileClip
import os
import subprocess
from pathlib import Path

def obtener_ruta_escritorio():
    posibles_rutas = [
        Path.home() / "OneDrive" / "Escritorio",
        Path.home() / "OneDrive" / "Desktop",
        Path.home() / "Escritorio",
        Path.home() / "Desktop"
    ]
    for ruta in posibles_rutas:
        if ruta.exists():
            return ruta
    raise FileNotFoundError("No se pudo encontrar la carpeta Escritorio.")



def actualizar_progreso(valor, texto=""):
    barra_progreso['value'] = valor
    etiqueta_estado.config(text=texto)
    ventana.update_idletasks()



def descargar_mp3():
    url = entrada_url.get()
    if not url:
        messagebox.showerror("Error", "Por favor, ingresa una URL válida.")
        return
    
    try:
        actualizar_progreso(0, "Preparando descarga...")
        download_path = Path(os.getcwd()) / "temp_audio"
        os.makedirs(download_path, exist_ok=True)

        actualizar_progreso(20, "Descargando audio con yt-dlp...")
            
        # Ruta de salida base
        salida_temp = download_path / "%(title)s.%(ext)s"

        # Comando yt-dlp
        comando = [
            "yt-dlp",
            "-f", "bestaudio",
            "-o", str(salida_temp),
            url
        ]

        resultado = subprocess.run(comando, capture_output=True, text=True)

        if resultado.returncode != 0:
            raise Exception(f"yt-dlp falló:\n{resultado.stderr}")

        actualizar_progreso(60, "Buscando archivo descargado...")

        # Buscar el archivo descargado
        archivo_m4a = next(download_path.glob("*.webm"), None)
        if archivo_m4a is None:
            archivo_m4a = next(download_path.glob("*.m4a"), None)
        if archivo_m4a is None:
            raise FileNotFoundError("No se encontró el archivo de audio descargado.")

        archivo_mp3 = archivo_m4a.with_suffix(".mp3")

        actualizar_progreso(75, "Convirtiendo a MP3...")
        clip = AudioFileClip(str(archivo_m4a))
        clip.write_audiofile(str(archivo_mp3))
        clip.close()

        actualizar_progreso(90, "Moviendo archivo final...")
        escritorio = obtener_ruta_escritorio()
        if not escritorio.exists():
            raise FileNotFoundError("No se pudo encontrar la carpeta Escritorio.")
        carpeta_salida = escritorio / "Descargas_MP3"
        
        if not carpeta_salida.exists():
            carpeta_salida.mkdir(parents=True, exist_ok=True)

        destino = carpeta_salida / archivo_mp3.name
        os.replace(archivo_mp3, destino)
        os.remove(archivo_m4a)

        actualizar_progreso(100, "¡Completado!")
        messagebox.showinfo("Éxito", f"Audio guardado en:\n{destino}")
        actualizar_progreso(0, "Listo para otra descarga.")

    except Exception as e:
        actualizar_progreso(0, "Error")
        messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
        print(f"Error: {e}")

# Interfaz gráfica con Tkinter
ventana = tk.Tk()
ventana.title("YouTube a MP3 con yt-dlp")
ventana.geometry("500x250")

etiqueta = tk.Label(ventana, text="URL de YouTube Music o YouTube:")
etiqueta.pack(pady=10)

entrada_url = tk.Entry(ventana, width=60)
entrada_url.pack(pady=5)

boton_descargar = tk.Button(ventana, text="Descargar MP3", command=descargar_mp3)
boton_descargar.pack(pady=10)

barra_progreso = ttk.Progressbar(ventana, orient="horizontal", length=400, mode="determinate")
barra_progreso.pack(pady=10)

etiqueta_estado = tk.Label(ventana, text="Listo para comenzar.")
etiqueta_estado.pack()

ventana.mainloop()
        