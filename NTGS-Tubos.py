#!/usr/bin/env python3

import sys
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os

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

def cargar_archivo():
	global df, max_x, max_y
	
	file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
	if not file_path:
		return
	
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
	
	# Cargar datos en un DataFrame
	data_csv = "".join(data_lines)
	df = pd.read_csv(pd.io.common.StringIO(data_csv), sep=';', skiprows=1)
	df.columns = ["Tiempo (s)", "Presión (MPa)"]
	
	# Mostrar datos en la tabla
	for row in tree.get_children():
		tree.delete(row)
	for _, row in df.iterrows():
		tree.insert("", tk.END, values=(row["Tiempo (s)"], row["Presión (MPa)"]))
		
	# Encontrar el máximo de presión
	max_index = df["Presión (MPa)"].idxmax()
	max_x = df.loc[max_index, "Tiempo (s)"]
	max_y = df.loc[max_index, "Presión (MPa)"]
	
	# Graficar los datos
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
	ax.set_title("Curva de presión del sensor Kistler")
	ax.legend()
	ax.grid()
	
	plt.draw()  # Redibujar la gráfica sin abrir una nueva ventana
	plt.pause(0.1)  # Pequeña pausa para actualizar la visualización
	
# Configuración de la ventana principal
def main():
	global root, metadata_text, tree
	
	root = tk.Tk()
	root.title("Visor de Datos Kistler")
	root.geometry("800x600")
	
	# Botón para cargar archivo
	btn_cargar = tk.Button(root, text="Cargar Archivo CSV", command=cargar_archivo)
	btn_cargar.pack(pady=10)
	
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
