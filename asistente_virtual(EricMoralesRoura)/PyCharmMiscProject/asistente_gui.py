import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def cargar_contexto():
        with open("servicios.txt", "r", encoding="utf-8") as f:
            return f.read()
contexto = cargar_contexto()

def obtener_respuesta():
    pregunta = entrada.get().strip()
    if not pregunta:
        salida.insert(tk.END, "Por favor, escribe una pregunta.\n\n")
        return

    salida.insert(tk.END, f"Tú: {pregunta}\n", "usuario")
    entrada.delete(0, tk.END)

    try:
        prompt = f"""
        Eres un asistente virtual amable de una peluquería.
        Usa la siguiente información como referencia para responder:

        {contexto}

        Cliente: {pregunta}
        """

        respuesta = model.generate_content(prompt)

        texto_respuesta = respuesta.text.strip()
        salida.insert(tk.END, f"Asistente: {texto_respuesta}\n\n", "asistente")

    except Exception as e:
        salida.insert(tk.END, f"Error al obtener respuesta: {e}\n\n")

ventana = tk.Tk()
ventana.title("Asistente Virtual - Peluquería Belleza Total")
ventana.geometry("1200x600")
ventana.configure(bg="#292929")

titulo = tk.Label(ventana, text="Asistente Virtual de Peluquería", font=("Arial", 16, "bold"), bg="#292929", fg="white")
titulo.pack(pady=10)

salida = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=70, height=20, bg="#171717", fg="#333")
salida.pack(padx=10, pady=10)
salida.tag_config("usuario", foreground="white", font=("Arial", 10, "bold"))
salida.tag_config("asistente", foreground="#95ff87", font=("Arial", 10))

entrada = tk.Entry(ventana, width=60, font=("Arial", 12), bg="#171717", fg="white")
entrada.pack(pady=5)

boton = tk.Button(ventana, text="Enviar", command=obtener_respuesta, bg="#ff9124", fg="white", font=("Arial", 12, "bold"))
boton.pack(pady=5)

ventana.mainloop()

