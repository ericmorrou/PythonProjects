import os
from dominio.Alumno import Alumno

class AlumnosMatriculados:
    ruta_archivo: str = "alumnos.txt"

    @staticmethod
    def matricular_alumno(alumno):
        if isinstance(alumno, Alumno):
            texto = alumno.nombre
        else:
            texto = str(alumno)

        with open(AlumnosMatriculados.ruta_archivo, "a", encoding="utf-8") as f:
            f.write(texto + "\n")


        print(f"Alumno '{texto}' matriculado correctamente.")

    @staticmethod
    def listar_alumnos():
        if not os.path.exists(AlumnosMatriculados.ruta_archivo):
            print("No hay alumnos matriculados todavía.")
            return []

        with open(AlumnosMatriculados.ruta_archivo, "r", encoding="utf-8") as f:
            alumnos = [line.strip() for line in f if line.strip()]

        if alumnos:
            print("\nAlumnos matriculados:")
            for alumno in alumnos:
                print(f" - {alumno}")
        else:
            print("No hay alumnos matriculados.")

        return alumnos

    @staticmethod
    def eliminar_alumnos():
        open(AlumnosMatriculados.ruta_archivo, "w", encoding="utf-8").close()
        print("Todos los alumnos han sido eliminados.")
