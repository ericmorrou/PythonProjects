import psycopg2
from src.conexion_db import ConexionDB
import json
from datetime import datetime, timedelta

class AuthDAO:
    def __init__(self):
        self.db = ConexionDB()

    def registrar_usuario(self, username, passphrase_text, log_json):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Insertar usuario
                cur.execute("""
                    INSERT INTO usuarios_voz (username, passphrase_text)
                    VALUES (%s, %s)
                    RETURNING id
                """, (username, passphrase_text))
                user_id = cur.fetchone()[0]

                # 2. Insertar log inicial
                cur.execute("""
                    INSERT INTO log_accesos_voz (usuario_id, resultado_json)
                    VALUES (%s, %s)
                """, (user_id, json.dumps(log_json)))
                
                conn.commit()
                return True, "Usuario registrado con éxito"
        except psycopg2.IntegrityError:
            conn.rollback()
            return False, "El usuario ya existe"
        except Exception as e:
            conn.rollback()
            return False, f"Error en registro: {e}"

    def obtener_usuario(self, username):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, passphrase_text, intentos_fallidos, bloqueado_hasta
                    FROM usuarios_voz
                    WHERE username = %s
                """, (username,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None

    def registrar_login(self, user_id, exito, log_json, bloquear=False):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                # Insertar Log
                cur.execute("""
                    INSERT INTO log_accesos_voz (usuario_id, resultado_json)
                    VALUES (%s, %s)
                """, (user_id, json.dumps(log_json)))

                # Actualizar Usuario
                if exito:
                    cur.execute("""
                        UPDATE usuarios_voz 
                        SET intentos_fallidos = 0, bloqueado_hasta = NULL
                        WHERE id = %s
                    """, (user_id,))
                else:
                    if bloquear:
                         # Bloqueo por 1 minuto para prueba
                         bloqueo_time = datetime.now() + timedelta(minutes=1)
                         cur.execute("""
                            UPDATE usuarios_voz 
                            SET intentos_fallidos = intentos_fallidos + 1,
                                bloqueado_hasta = %s
                            WHERE id = %s
                        """, (bloqueo_time, user_id))
                    else:
                        cur.execute("""
                            UPDATE usuarios_voz 
                            SET intentos_fallidos = intentos_fallidos + 1
                            WHERE id = %s
                        """, (user_id,))
                
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error al registrar login: {e}")

    def obtener_logs_criticos(self):
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT u.username, l.resultado_json
                    FROM log_accesos_voz l 
                    JOIN usuarios_voz u ON l.usuario_id = u.id 
                    WHERE l.resultado_json->>'status' = 'FAIL'
                       OR (l.resultado_json->>'confianza')::float < 0.6
                    ORDER BY l.fecha_intento DESC
                """)
                return cur.fetchall()
        except Exception as e:
            print(f"Error al obtener logs: {e}")
            return []
