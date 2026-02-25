import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import os

# Add parent directory to path so 'src' module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.voice_service import VoiceService
from src.auth_dao import AuthDAO
from datetime import datetime

class VoiceAuditApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VoiceAudit - Acceso por Voz")
        self.root.geometry("600x500")
        
        self.voice_service = VoiceService()
        self.auth_dao = AuthDAO()

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_login_frame()

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_frame(self):
        self.clear_frame()
        
        tk.Label(self.container, text="Login de Voz", font=("Helvetica", 16)).pack(pady=10)
        
        tk.Label(self.container, text="Usuario:").pack()
        self.username_entry = tk.Entry(self.container)
        self.username_entry.pack(pady=5)

        tk.Button(self.container, text="🎤 Entrar con Voz", command=self.perform_login, bg="#e1f5fe").pack(pady=10)
        
        tk.Button(self.container, text="Registrar Nuevo Usuario", command=self.show_register_frame).pack(pady=5)
        tk.Button(self.container, text="⚠️ Panel de Auditoría", command=self.show_audit_frame, fg="red").pack(pady=5)

        self.status_label = tk.Label(self.container, text="", fg="blue")
        self.status_label.pack(pady=10)

    def show_register_frame(self):
        self.clear_frame()
        
        tk.Label(self.container, text="Registro de Usuario", font=("Helvetica", 16)).pack(pady=10)
        
        tk.Label(self.container, text="Nombre de Usuario:").pack()
        self.reg_username_entry = tk.Entry(self.container)
        self.reg_username_entry.pack(pady=5)

        tk.Button(self.container, text="🎤 Grabar Frase de Paso", command=self.perform_register, bg="#e1f5fe").pack(pady=10)
        
        tk.Button(self.container, text="Volver", command=self.show_login_frame).pack(pady=5)
        
        self.reg_status_label = tk.Label(self.container, text="", fg="blue")
        self.reg_status_label.pack(pady=10)

    def show_audit_frame(self):
        self.clear_frame()
        
        tk.Label(self.container, text="Auditoría de Accesos (Fallos/Baja Confianza)", font=("Helvetica", 14)).pack(pady=10)
        
        self.audit_text = scrolledtext.ScrolledText(self.container, height=15, width=60)
        self.audit_text.pack(pady=10)
        
        btn_frame = tk.Frame(self.container)
        btn_frame.pack()
        
        tk.Button(btn_frame, text="Refrescar Datos", command=self.load_audit_logs).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Volver", command=self.show_login_frame).pack(side="left", padx=5)

        self.load_audit_logs()

    def perform_register(self):
        username = self.reg_username_entry.get().strip()
        if not username:
            messagebox.showwarning("Error", "El nombre de usuario es obligatorio.")
            return

        self.reg_status_label.config(text="Escuchando... Di tu frase.")
        self.root.update()

        texto, meta = self.voice_service.capturar_voz()
        
        if not texto:
            self.reg_status_label.config(text=f"Error: {meta.get('reason', 'Desconocido')}")
            return

        if messagebox.askyesno("Confirmar Frase", f"Se escuchó: '{texto}'\n¿Es correcto?"):
            exito, mensaje = self.auth_dao.registrar_usuario(username, texto, meta)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.show_login_frame()
            else:
                self.reg_status_label.config(text=f"Error en BD: {mensaje}")
        else:
            self.reg_status_label.config(text="Registro cancelado. Intenta de nuevo.")

    def perform_login(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Error", "Introduce tu usuario.")
            return

        # 1. Verificar usuario en BD
        user_data = self.auth_dao.obtener_usuario(username)
        if not user_data:
            # Para seguridad, a veces es mejor no decir si existe o no, 
            # pero para la práctica mostramos error claro o simulamos fallo de voz.
            # Aquí diremos "Usuario no encontrado" para facilitar pruebas.
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        user_id, stored_passphrase, intentos, bloqueado_hasta = user_data

        # 2. Verificar bloqueo
        if bloqueado_hasta and bloqueado_hasta > datetime.now():
            messagebox.showerror("Bloqueado", f"Usuario bloqueado hasta {bloqueado_hasta}")
            return

        self.status_label.config(text="Escuchando... Di tu frase.")
        self.root.update()

        # 3. Capturar voz
        texto, meta = self.voice_service.capturar_voz()
        
        if not texto:
            self.status_label.config(text=f"Error de voz: {meta.get('reason')}")
            # Considerar si esto cuenta como intento fallido. 
            # Si es ruido/silencio, quizás no. Si es "no entendido", quizás sí.
            # Para simplificar, solo fallamos si hay texto incorrecto.
            return

        # 4. Validar frase
        # Normalización básica (minúsculas, espacios)
        es_correcto = (texto.lower().strip() == stored_passphrase.lower().strip())
        
        # Lógica de bloqueo
        bloquear = False
        if not es_correcto:
            # Si intentos actuales (antes de este fallo) son 2, ahora serán 3 -> Bloqueo
            if intentos >= 2: 
                bloquear = True
                meta["bloqueado"] = True
            
            meta["frase_intentada"] = texto
            meta["intentos_restantes"] = 2 - intentos if intentos < 3 else 0

        self.auth_dao.registrar_login(user_id, es_correcto, meta, bloquear)

        if es_correcto:
            self.status_label.config(text="¡Acceso Concedido!", fg="green")
            messagebox.showinfo("Bienvenido", f"Hola {username}, acceso autorizado.\nConfianza: {meta.get('confianza', 0)}")
        else:
            msg = "Frase incorrecta."
            if bloquear:
                msg += "\nCUENTA BLOQUEADA TEMPORALMENTE."
            self.status_label.config(text="¡Acceso Denegado!", fg="red")
            messagebox.showerror("Error", msg)

    def load_audit_logs(self):
        self.audit_text.delete(1.0, tk.END)
        logs = self.auth_dao.obtener_logs_criticos()
        if not logs:
            self.audit_text.insert(tk.END, "No hay logs críticos recientes.")
            return

        for user, log_json in logs:
            # log_json is already a dict if fetched via psycopg2 with correct type handling,
            # or usage in DAO implies it might be dict or string. 
            # psycopg2 Returns dict for JSONB if configured, or string.
            # Let's assume usage of psycopg2 standard which returns dict for jsonb in recent versions 
            # or ensure we cast it if needed. 
            # In auth_dao we selected 'resultado_json' which is JSONB.
            
            # Simple display
            self.audit_text.insert(tk.END, f"User: {user}\nData: {log_json}\n" + "-"*40 + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAuditApp(root)
    root.mainloop()
