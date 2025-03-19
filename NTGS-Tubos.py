#!/usr/bin/env python3

import sys
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Ajustar el backend de Matplotlib para Windows
matplotlib.use("TkAgg")

# Función para detectar si se ejecuta desde un archivo .exe
def resource_path(relative_path):
    """Retorna la ruta absoluta del recurso, compatible con PyInstaller"""
    if getattr(sys, 'frozen', False):  # Si el script está compilado con PyInstaller
        base_path = sys._MEIPASS  # Carpeta temporal de PyInstaller
    else:
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)

# Crear figura y eje global para mantener la misma ventana abierta
fig, ax = plt.subplots(figsize=(10, 5))
plt.ion()  # Modo interactivo para actualizar la gráfica sin abrir nuevas ventanas

def modificar_guardado(fig):
    """Modifica el botón de guardado para que use el nombre del archivo CSV por defecto."""
    from matplotlib.backends.backend_pdf import PdfPages
    import tkinter.filedialog as fd

    def guardar_personalizado():
        global file_name
        if not file_name:
            file_name = "Figura"  # Valor por defecto si no hay CSV cargado

        default_name = f"{file_name}.png"  # Nombre por defecto con extensión .png
        file_path = fd.asksaveasfilename(defaultextension=".png",
                                         initialfile=default_name,
                                         filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("PDF", "*.pdf"),
                                                    ("SVG", "*.svg"), ("Todos los archivos", "*.*")])
        if file_path:
            if file_path.endswith(".pdf"):
                with PdfPages(file_path) as pdf:
                    pdf.savefig(fig)
            else:
                fig.savefig(file_path)

    # Reemplazar el comportamiento del botón de guardado de Matplotlib
    fig.canvas.manager.toolbar.save_figure = guardar_personalizado

def guardar_como_imagen():
    """Permite guardar la gráfica con el nombre del archivo CSV cargado."""
    global file_name
    if not file_name:
        file_name = "Figura"

    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             initialfile=f"{file_name}.png",
                                             filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("PDF", "*.pdf"),
                                                        ("SVG", "*.svg"), ("Todos los archivos", "*.*")])
    if file_path:
        fig.savefig(file_path)

def guardar_rapido():
    """Guarda automáticamente la gráfica en la misma carpeta del CSV con el mismo nombre."""
    global file_name, csv_path
    if not file_name or not csv_path:
        return  # No hacer nada si no hay un archivo cargado

    output_path = os.path.join(os.path.dirname(csv_path), f"{file_name}.jpg")
    fig.savefig(output_path, format="jpg")
    print(f"Gráfica guardada en: {output_path}")  # Mensaje para depuración

def cargar_archivo():
    global df, max_x, max_y, file_name, csv_path
    
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    if not file_path:
        return

    csv_path = file_path  # Guardar la ruta completa del archivo CSV
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Extraer metadatos (antes de la línea de datos)
    metadata = []
    data_lines = []
    data_started = False

    for line in lines:
        if "Time;" in line:
            data_started = True
        if data_started:
            data_lines.append(line)
        else:
            metadata.append(line.strip())

    # Mostrar metadatos en el cuadro de texto
    metadata_text.config(state=tk.NORMAL)
    metadata_text.delete(1.0, tk.END)
    metadata_text.insert(tk.END, "\n".join(metadata))
    metadata_text.config(state=tk.DISABLED)

    # Limpiar la tabla antes de agregar nuevos datos
    for row in tree.get_children():
        tree.delete(row)

    # Cargar datos en un DataFrame
    data_csv = "".join(data_lines)
    df = pd.read_csv(pd.io.common.StringIO(data_csv), sep=';', skiprows=1)
    df.columns = ["Tiempo (s)", "Presión (MPa)"]

    # Agregar los datos a la tabla
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=(row["Tiempo (s)"], row["Presión (MPa)"]))

    # Encontrar el máximo de presión
    max_index = df["Presión (MPa)"].idxmax()
    max_x = df.loc[max_index, "Tiempo (s)"]
    max_y = df.loc[max_index, "Presión (MPa)"]

    # Graficar los datos
    actualizar_grafica()

def mostrar_grafica():
    """Reabre la ventana de Matplotlib si se ha cerrado."""
    global fig, ax
    if not plt.fignum_exists(fig.number):  # Verifica si la ventana sigue abierta
        fig, ax = plt.subplots(figsize=(10, 5))
        plt.ion()
        actualizar_grafica()

def on_tree_select(event):
    global selected_x, selected_y
    selected_item = tree.selection()
    
    if selected_item:
        item_values = tree.item(selected_item[0], "values")
        selected_x = float(item_values[0])
        selected_y = float(item_values[1])
        actualizar_grafica()
        
def actualizar_grafica():
    ax.clear()  # Limpiar la gráfica sin abrir una nueva ventana
    ax.plot(df["Tiempo (s)"], df["Presión (MPa)"], label="Presión", color="b")
    ax.scatter(max_x, max_y, color="r", label=f"Máx: {max_y:.2f} MPa en {max_x:.6f} s")
    
    # Pintar punto seleccionado en verde
    if 'selected_x' in globals() and 'selected_y' in globals():
        ax.scatter(selected_x, selected_y, color="g", label=f"Sel: {selected_y:.2f} MPa en {selected_x:.6f} s")
        
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Presión (MPa)")
    ax.set_title(f"Curva de presión: {file_name}")  # Cambiar título por el nombre del archivo
    ax.legend()
    ax.grid()
    
    plt.draw()  # Redibujar la gráfica sin abrir una nueva ventana
    plt.pause(0.1)  # Pequeña pausa para actualizar la visualización
    
    # Personalizar el guardado con el nombre del CSV
    modificar_guardado(fig)

# Configuración de la ventana principal
def main():
    global root, metadata_text, tree
    
    root = tk.Tk()
    root.title("Visor de Datos Kistler")
    root.geometry("800x600")
    
    # Frame para organizar los botones en una línea
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Botón para cargar archivo
    btn_cargar = tk.Button(button_frame, text="Cargar Archivo CSV", command=cargar_archivo)
    btn_cargar.pack(side=tk.LEFT, padx=5)

    # Botón para mostrar la gráfica
    btn_mostrar_grafica = tk.Button(button_frame, text="Mostrar Gráfica", command=mostrar_grafica)
    btn_mostrar_grafica.pack(side=tk.LEFT, padx=5)

    # Botón para guardar la gráfica como imagen
    btn_guardar_grafica = tk.Button(button_frame, text="Guardar Gráfica", command=guardar_como_imagen)
    btn_guardar_grafica.pack(side=tk.LEFT, padx=5)

    # Botón para guardar rápidamente
    btn_guardar_rapido = tk.Button(button_frame, text="Guardar Rápido", command=guardar_rapido)
    btn_guardar_rapido.pack(side=tk.LEFT, padx=5)
    
    # Cuadro de texto para metadatos
    metadata_text = scrolledtext.ScrolledText(root, height=10, state=tk.DISABLED)
    metadata_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # Tabla para datos de presión
    tree = ttk.Treeview(root, columns=("Tiempo (s)", "Presión (MPa)"), show="headings")
    tree.heading("Tiempo (s)", text="Tiempo (s)")
    tree.heading("Presión (MPa)", text="Presión (MPa)")
    tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # Evento para detectar selección en la tabla
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    
    root.mainloop()
    
# Asegurar que el programa no se cierre inmediatamente en Windows al compilarse con PyInstaller
if __name__ == "__main__":
    main()
