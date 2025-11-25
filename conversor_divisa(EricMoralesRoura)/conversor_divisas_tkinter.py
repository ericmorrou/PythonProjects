#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from decimal import Decimal, InvalidOperation

ECB_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

def descargar_xml(url: str) -> bytes:
    """
    Descarga el contenido XML desde la URL del BCE.
    Devuelve bytes del contenido si la petición es exitosa.
    Lanza excepción si hay problema de conexión o código HTTP distinto de 200.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        raise RuntimeError(f"Error descargando datos: {e}")

def parsear_tasas(xml_bytes: bytes) -> tuple:
    """
    Parsear el XML proporcionado por el BCE y extraer:
      - fecha (atributo time del nodo <Cube>)
      - diccionario { 'USD': Decimal('1.0683'), ... }
    Añade manualmente 'EUR': Decimal('1.0').
    """
    root = ET.fromstring(xml_bytes)

    ns = {
        'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
        'def': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'
    }

    time_cube = root.find('.//def:Cube[@time]', ns)
    if time_cube is None:
        raise RuntimeError("No se encontró el nodo <Cube time=\"...\"> en el XML.")

    fecha = time_cube.attrib.get('time')
    tasas = {}

    for c in time_cube.findall('def:Cube', ns):
        moneda = c.attrib.get('currency')
        rate = c.attrib.get('rate')
        if moneda is None or rate is None:
            continue
        try:
            tasas[moneda] = Decimal(rate)
        except InvalidOperation:
            raise RuntimeError(f"Tasa inválida para {moneda}: {rate}")

    tasas['EUR'] = Decimal('1.0')

    return fecha, tasas

def convertir(import_amount: Decimal, origen: str, destino: str, tasas: dict) -> Decimal:
    """
    Convierte `import_amount` desde `origen` a `destino` usando el diccionario `tasas`.
    Fórmula: cantidad_final = (importe / tasa_origen) * tasa_destino
    Donde cada tasa es X unidades de moneda por 1 EUR (1 EUR = tasa moneda).
    """
    if origen not in tasas:
        raise KeyError(f"Moneda origen desconocida: {origen}")
    if destino not in tasas:
        raise KeyError(f"Moneda destino desconocida: {destino}")

    tasa_origen = tasas[origen]
    tasa_destino = tasas[destino]

    if tasa_origen == 0:
        raise ZeroDivisionError("La tasa de la moneda origen es 0, conversión imposible.")

    importe_en_eur = import_amount / tasa_origen
    resultado = importe_en_eur * tasa_destino
    return resultado

class ConversorApp:
    def __init__(self, root):
        """
        Inicializa la GUI, descarga las tasas y prepara los widgets.
        root: instancia de tk.Tk()
        """
        self.root = root
        self.root.title("Conversor de Divisas - BCE (XML)")

        main = ttk.Frame(root, padding="12 12 12 12")
        main.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.cantidad_var = tk.StringVar()
        self.origen_var = tk.StringVar()
        self.destino_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.fecha_var = tk.StringVar()

        ttk.Label(main, text="Importe:").grid(column=1, row=1, sticky=tk.W)
        self.entry_importe = ttk.Entry(main, width=20, textvariable=self.cantidad_var)
        self.entry_importe.grid(column=2, row=1, sticky=(tk.W, tk.E))
        self.entry_importe.insert(0, "1.00")

        ttk.Label(main, text="Moneda origen:").grid(column=1, row=2, sticky=tk.W)
        self.combo_origen = ttk.Combobox(main, textvariable=self.origen_var, state="readonly")
        self.combo_origen.grid(column=2, row=2, sticky=(tk.W, tk.E))

        ttk.Label(main, text="Moneda destino:").grid(column=1, row=3, sticky=tk.W)
        self.combo_destino = ttk.Combobox(main, textvariable=self.destino_var, state="readonly")
        self.combo_destino.grid(column=2, row=3, sticky=(tk.W, tk.E))

        self.btn_convertir = ttk.Button(main, text="Convertir", command=self.accion_convertir)
        self.btn_convertir.grid(column=2, row=4, sticky=tk.E)

        ttk.Label(main, text="Resultado:").grid(column=1, row=5, sticky=tk.W)
        self.lbl_resultado = ttk.Label(main, textvariable=self.result_var, font=("TkDefaultFont", 11, "bold"))
        self.lbl_resultado.grid(column=2, row=5, sticky=(tk.W, tk.E))

        ttk.Label(main, text="Fecha datos:").grid(column=1, row=6, sticky=tk.W)
        self.lbl_fecha = ttk.Label(main, textvariable=self.fecha_var)
        self.lbl_fecha.grid(column=2, row=6, sticky=(tk.W, tk.E))

        self.btn_recargar = ttk.Button(main, text="Recargar tasas", command=self.recargar_tasas)
        self.btn_recargar.grid(column=1, row=4, sticky=tk.W)

        for child in main.winfo_children():
            child.grid_configure(padx=8, pady=6)

        self.tasas = {}

        try:
            self.cargar_tasas_automatica()
        except Exception as e:
            messagebox.showwarning("Atención", f"No se pudieron cargar las tasas automáticamente:\n{e}\nPuedes intentarlo con 'Recargar tasas'.")
            self.tasas = {'EUR': Decimal('1.0')}
            monedas = sorted(self.tasas.keys())
            self.combo_origen['values'] = monedas
            self.combo_destino['values'] = monedas
            self.origen_var.set('EUR')
            self.destino_var.set('EUR')
            self.fecha_var.set("Desconocida")

    def cargar_tasas_automatica(self):
        """Descarga el XML y carga las tasas en la GUI; lanzará excepción si hay problema."""
        xml_bytes = descargar_xml(ECB_URL)
        fecha, tasas = parsear_tasas(xml_bytes)
        self.tasas = tasas
        monedas = sorted(self.tasas.keys())
        self.combo_origen['values'] = monedas
        self.combo_destino['values'] = monedas
        if 'EUR' in monedas:
            self.origen_var.set('EUR')
            self.destino_var.set('USD' if 'USD' in monedas else 'EUR')
        else:
            # fallback
            self.origen_var.set(monedas[0])
            self.destino_var.set(monedas[0])

        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            self.fecha_var.set(fecha_dt.strftime("%Y-%m-%d"))
        except Exception:
            self.fecha_var.set(str(fecha))

    def recargar_tasas(self):
        """Acción manual para recargar las tasas desde el BCE."""
        try:
            self.cargar_tasas_automatica()
            messagebox.showinfo("Tasas recargadas", "Tasas actualizadas correctamente desde el BCE.")
        except Exception as e:
            messagebox.showerror("Error recargando", f"No se pudo recargar las tasas:\n{e}")

    def accion_convertir(self):
        """
        Evento disparado al pulsar 'Convertir'.
        Realiza validaciones de entrada, llama a la función de conversión y muestra el resultado.
        """
        importe_texto = self.cantidad_var.get().strip()  # obtenemos texto ingresado
        origen = self.origen_var.get()
        destino = self.destino_var.get()

        if importe_texto == "":
            messagebox.showerror("Error", "Introduce un importe numérico.")
            return

        try:
            importe_texto_normalizado = importe_texto.replace(',', '.')
            importe_decimal = Decimal(importe_texto_normalizado)
        except InvalidOperation:
            messagebox.showerror("Error", "Importe no válido. Usa sólo números (por ejemplo: 123.45).")
            return

        if origen == "" or destino == "":
            messagebox.showerror("Error", "Selecciona la moneda de origen y destino.")
            return

        try:
            resultado = convertir(importe_decimal, origen, destino, self.tasas)
        except Exception as e:
            messagebox.showerror("Error en conversión", f"No se pudo convertir: {e}")
            return

        resultado_str = f"{importe_decimal} {origen} = {resultado.quantize(Decimal('0.000001'))} {destino}"
        self.result_var.set(resultado_str)

def main():
    """Función principal para lanzar la aplicación."""
    root = tk.Tk()
    app = ConversorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
