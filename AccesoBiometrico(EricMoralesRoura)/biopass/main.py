
import tkinter as tk
from tkinter import messagebox, simpledialog
from dao import UsuarioDAO
import cv2
from PIL import Image, ImageTk
import numpy as np

class BioPassApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BioPass - Acceso Biométrico")
        self.dao = UsuarioDAO()
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        import os
        ruta_cascade = os.path.join(os.path.dirname(os.path.abspath(__file__)), "haarcascade_frontalface_default.xml")
        self.face_cascade = cv2.CascadeClassifier(ruta_cascade)
        print('¿Clasificador cargado?', not self.face_cascade.empty())
        self.label = tk.Label(root)
        self.label.pack()
        tk.Button(root, text='Registrar', command=self.registrar_usuario).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(root, text='Verificar', command=self.verificar_usuario).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(root, text='Salir', command=self.salir).pack(side=tk.LEFT, padx=10, pady=10)


        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame = frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
        self.root.after(20, self.update_frame)

    def registrar_usuario(self):
        if self.frame is None:
            messagebox.showerror('Error', 'No hay imagen de cámara disponible')
            return
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        if len(faces) == 0:
            messagebox.showerror('Error', 'No se detectó ninguna cara. Intenta de nuevo.')
            return
        (x, y, w, h) = faces[0]
        cara = gray[y:y+h, x:x+w]
        cara = cv2.resize(cara, (200, 200))
        nombre = simpledialog.askstring('Nombre', 'Introduce el nombre del usuario:')
        if not nombre:
            return
        _, buffer = cv2.imencode('.jpg', cara)
        imagen_bytes = buffer.tobytes()
        try:
            self.dao.guardar_usuario(nombre, imagen_bytes)
            messagebox.showinfo('Éxito', 'Usuario registrado correctamente')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo guardar el usuario: {e}')

    def verificar_usuario(self):
        if self.frame is None:
            messagebox.showerror('Error', 'No hay imagen de cámara disponible')
            return
        usuarios = self.dao.obtener_usuarios()
        if not usuarios:
            messagebox.showwarning('Sin datos', 'No hay usuarios registrados')
            return
        faces = []
        labels = []
        nombres = {}
        for idx, (id, nombre, imagen_bytes) in enumerate(usuarios):
            arr = np.frombuffer(imagen_bytes, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces.append(img)
                labels.append(idx)
                nombres[idx] = nombre
        if not faces:
            messagebox.showwarning('Sin datos', 'No hay imágenes válidas para comparar')
            return
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        caras = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        if len(caras) == 0:
            messagebox.showerror('Error', 'No se detectó ninguna cara para verificar.')
            return
        (x, y, w, h) = caras[0]
        cara = gray[y:y+h, x:x+w]
        cara = cv2.resize(cara, (200, 200))
        label, confidence = recognizer.predict(cara)
        UMBRAL = 60
        if confidence < UMBRAL:
            nombre = nombres.get(label, 'Desconocido')
            messagebox.showinfo('Resultado', f'Usuario reconocido: {nombre}')
        else:
            messagebox.showinfo('Resultado', f'Usuario no reconocido')

    def salir(self):
        self.cap.release()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = BioPassApp(root)
    root.mainloop()