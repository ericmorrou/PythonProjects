from dominio.Alumno import Alumno
from servicio.AlumnosMatriculados import AlumnosMatriculados

def mostrar_menu():
    print("\n=== GESTIÓN DE MATRÍCULAS ===")
    print("1. Matricular alumno")
    print("2. Mostrar alumnos matriculados")
    print("3. Eliminar archivo de alumnos")
    print("4. Salir")
    opcion = input("Selecciona una opción: ")
    return opcion


def main():
    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            nombre = input("Introduce el nombre del alumno: ").strip()
            if nombre:
                alumno = Alumno(nombre)
                AlumnosMatriculados.matricular_alumno(alumno)
            else:
                print("El nombre no puede estar vacío.")

        elif opcion == "2":
            AlumnosMatriculados.listar_alumnos()

        elif opcion == "3":
            confirmar = input("¿Estás seguro de que deseas eliminar todos los alumnos? (s/n): ").lower()
            if confirmar == "s":
                AlumnosMatriculados.eliminar_alumnos()
            else:
                print("Operación cancelada.")

        elif opcion == "4":
            print("Saliendo del programa...")
            break

        else:
            print("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main()
