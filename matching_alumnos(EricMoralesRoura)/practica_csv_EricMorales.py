import csv
import os

def leer_csv_DictReader(nombre_archivo):
    datos = []
    encodings = ['utf-8', 'windows-1252', 'iso-8859-1', 'cp1252']

    for encoding in encodings:
        try:
            with open(nombre_archivo, 'r', encoding=encoding, newline='') as archivo:
                lector = csv.DictReader(archivo, delimiter=';')
                datos = list(lector)
            print(f"{nombre_archivo} leído correctamente: {len(datos)} filas (encoding: {encoding})")
            return datos
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Error: No se encontró {nombre_archivo}")
            return []
        except Exception as e:
            print(f"Error al leer {nombre_archivo}: {e}")
            return []

    print(f"No se pudo leer {nombre_archivo} con ninguna codificación")
    return []


def combinar_notas(datos_uf1, datos_uf2):
    alumnos = {}

    for fila in datos_uf1:
        id_alumno = fila.get('Id', '').strip()
        if id_alumno:
            alumnos[id_alumno] = {
                'Id': id_alumno,
                'Nom': fila.get('Nom', '').strip(),
                'Cognoms': fila.get('Cognoms', '').strip(),
                'Nota_UF1': fila.get('Nota', '').strip(),
                'Nota_UF2': ''
            }

    for fila in datos_uf2:
        id_alumno = fila.get('Id', '').strip()
        if id_alumno:
            if id_alumno in alumnos:
                alumnos[id_alumno]['Nota_UF2'] = fila.get('Nota', '').strip()
            else:
                alumnos[id_alumno] = {
                    'Id': id_alumno,
                    'Nom': fila.get('Nom', '').strip(),
                    'Cognoms': fila.get('Cognoms', '').strip(),
                    'Nota_UF1': '',
                    'Nota_UF2': fila.get('Nota', '').strip()
                }

    return list(alumnos.values())


def escribir_csv(datos, nombre_archivo):
    try:
        campos = ['Id', 'Nom', 'Cognoms', 'Nota_UF1', 'Nota_UF2']
        with open(nombre_archivo, 'w', encoding='utf-8', newline='') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=campos, delimiter=';')
            escritor.writeheader()
            for alumno in datos:
                escritor.writerow(alumno)

        print(f"{nombre_archivo} creado correctamente: {len(datos)} registros")
        return True
    except Exception as e:
        print(f"Error al escribir {nombre_archivo}: {e}")
        return False


def mostrar_resumen(datos, titulo):
    print(f"\n{titulo}")
    print("="*50)

    total = len(datos)
    con_uf1 = sum(1 for a in datos if a['Nota_UF1'])
    con_uf2 = sum(1 for a in datos if a['Nota_UF2'])
    con_ambas = sum(1 for a in datos if a['Nota_UF1'] and a['Nota_UF2'])

    print(f"Total alumnos: {total}")
    print(f"Con nota UF1: {con_uf1}")
    print(f"Con nota UF2: {con_uf2}")
    print(f"Con ambas notas: {con_ambas}")

    if datos:
        print(f"\nPrimeros registros:")
        for i, alumno in enumerate(datos[:3]):
            uf1 = alumno['Nota_UF1'] or 'N/A'
            uf2 = alumno['Nota_UF2'] or 'N/A'
            print(f"   {i+1}. {alumno['Nom']} {alumno['Cognoms']} - UF1: {uf1}, UF2: {uf2}")


def verificar_archivos():
    archivo_uf1 = "Notas_Alumnos_UF1.csv"
    archivo_uf2 = "Notas_Alumnos_UF2.csv"

    if not os.path.exists(archivo_uf1):
        print(f"No se encontró {archivo_uf1}")
        return False

    if not os.path.exists(archivo_uf2):
        print(f"No se encontró {archivo_uf2}")
        return False

    return True


def main():
    if not verificar_archivos():
        print("\nAsegurate de tener los archivos:")
        print("- Notas_Alumnos_UF1.csv")
        print("- Notas_Alumnos_UF2.csv")
        print("en la misma carpeta que este programa\n")
        return

    datos_uf1 = leer_csv_DictReader("Notas_Alumnos_UF1.csv")
    datos_uf2 = leer_csv_DictReader("Notas_Alumnos_UF2.csv")

    if datos_uf1 or datos_uf2:
        datos_combinados = combinar_notas(datos_uf1, datos_uf2)
        escribir_csv(datos_combinados, "notas_alumnos.csv")
        mostrar_resumen(datos_combinados, "RESUMEN FINAL")

        print("\nPROCESAMIENTO COMPLETADO")
        print("Archivo generado: notas_alumnos.csv\n")
    else:
        print("No se pudieron leer los archivos de entrada")


if __name__ == "__main__":
    main()
