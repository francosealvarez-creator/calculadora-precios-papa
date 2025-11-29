import streamlit as st
import re

# Configuración de la página para que parezca una app en el cel
st.set_page_config(page_title="Calculadora Precios", layout="centered")

st.title("🍏 Calculadora de Precios")
st.write("Pega la lista del proveedor abajo:")

# 1. Entrada de datos
texto_entrada = st.text_area("Lista Original", height=200, placeholder="iPhone 13: 500\niPhone 14: 600...")

# Botón para procesar
if st.button("Calcular (+50 USD) 🚀", type="primary"):
    if texto_entrada:
        # 2. La lógica (Aquí es donde Python brilla)
        def sumar_precio(match):
            # Extrae el número, lo convierte a entero y suma 50
            precio_original = int(match.group())
            nuevo_precio = precio_original + 50
            return str(nuevo_precio)

        # Expresión regular: Busca números de 3 o 4 dígitos (ej: 400, 1200)
        # Esto evita sumar 50 al "14" de "iPhone 14" si no quieres.
        # Ajusta r'\b\d{3,4}\b' según los precios que maneje.
        texto_procesado = re.sub(r'\b\d{3,4}\b', sumar_precio, texto_entrada)

        # 3. Salida
        st.success("¡Listo! Copia el resultado:")
        st.code(texto_procesado, language=None)
    else:
        st.warning("Primero pega la lista arriba.")
