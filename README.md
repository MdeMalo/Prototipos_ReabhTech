# RehabTech - Prototipo de Ejercicios con IA

> **Nota:** Este proyecto se encuentra en fase de **prototipo**. No es un producto final, sino una base para desarrollo y pruebas.

## 📜 Descripción

**RehabTech** es un conjunto de prototipos que utilizan **Computer Vision** e **Inteligencia Artificial** para **asistir en terapias de rehabilitación física**, especialmente en el seguimiento de movimientos de brazos.

Estos prototipos permiten:
- Detectar y analizar el movimiento del brazo usando **MediaPipe Pose**.
- Calcular **ángulos articulares** en tiempo real.
- Validar si las **posturas** son correctas o incorrectas.
- Llevar un **contador de repeticiones** automáticamente.
- **Guardar datos** en archivos CSV para analizar el progreso.
- Mostrar un **asistente visual** animado que guía el ejercicio.

## 🎥 Tecnologías Utilizadas

- [Python 3](https://www.python.org/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://google.github.io/mediapipe/)
- [NumPy](https://numpy.org/)
- [CSV (para guardar registros)](https://docs.python.org/3/library/csv.html)

## 🛠 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/rehabtech-prototipos.git
   cd rehabtech-prototipos
   ```

2. Instala las dependencias:
   ```bash
   pip install opencv-python mediapipe numpy
   ```

3. Ejecuta el prototipo:
   ```bash
   python ejercicio_brazo.py
   ```

## ⚙️ ¿Cómo funciona?

- Abre la cámara web.
- Detecta la pose humana (enfocado en brazos).
- Calcula los ángulos de movimiento en tiempo real.
- Muestra un contador de repeticiones.
- Advierte si la postura no es adecuada.
- Guarda el historial de movimientos en un archivo CSV.
- Muestra un "stickman" animado como guía.

## 🧪 Estado del Proyecto

✅ Funcionalidad básica de detección y seguimiento  
✅ Registro de repeticiones y datos  
✅ Asistente visual animado  
❌ No validado clínicamente  
❌ No optimizado para múltiples tipos de ejercicios aún

## 📈 Futuras mejoras

- Añadir sonidos de retroalimentación al completar repeticiones.
- Generar gráficos de avance a partir de los CSVs.
- Crear más tipos de ejercicios (piernas, espalda, hombros).
- Desarrollar una interfaz de usuario (UI) más amigable.

## 📄 Licencia

Este prototipo es de **código abierto** y está disponible bajo la Licencia MIT.

---

# 🚀 Sobre RehabTech

**RehabTech** es una iniciativa para crear tecnologías accesibles que ayuden en procesos de **rehabilitación física desde casa**, usando inteligencia artificial y sensores de bajo costo.
