from conexion import Conexion

class UsuarioDAO:
    def __init__(self):
        self.conn = Conexion().get_connection()

    def guardar_usuario(self, nombre, imagen_bytes):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (nombre, imagen) VALUES (%s, %s)
            """, (nombre, imagen_bytes))
            self.conn.commit()

    def obtener_usuarios(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, nombre, imagen FROM usuarios")
            return cur.fetchall()
