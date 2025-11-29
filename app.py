import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Generador de Lista", layout="centered")

st.title("🍏 Lista de Precios en Imagen")
st.write("Pega la lista, calcula y descarga la imagen para WhatsApp.")

# 1. Entrada de datos
texto_entrada = st.text_area("Lista Original", height=150, placeholder="iPhone 13: 500\niPhone 14: 600...")

# --- FUNCIÓN PARA CREAR IMAGEN ---
def crear_imagen(texto_lista):
    # Definir colores y tamaños
    color_fondo = (255, 255, 255) # Blanco
    color_texto = (0, 0, 0)       # Negro
    ancho_imagen = 800
    
    # Intentar cargar una fuente bonita (si no hay, usa la default)
    try:
        # Si subes un archivo de fuente (ej: arial.ttf) al repo, pon su nombre aquí
        font = ImageFont.truetype("arial.ttf", 40)
        font_titulo = ImageFont.truetype("arial.ttf", 60)
        padding_linea = 10
    except:
        # Fuente por defecto (es fea pero funciona si no subes un archivo .ttf)
        font = ImageFont.load_default()
        font_titulo = font
        padding_linea = 4

    # Calcular la altura necesaria de la imagen según la cantidad de líneas
    lineas = texto_lista.split('\n')
    # Altura base (título) + (alto de línea * cantidad) + márgenes
    alto_linea = font.getbbox("A")[3] + padding_linea 
    alto_imagen = 150 + (len(lineas) * alto_linea)

    # Crear el lienzo
    img = Image.new('RGB', (ancho_imagen, alto_imagen), color=color_fondo)
    d = ImageDraw.Draw(img)

    # Dibujar Título
    d.text((50, 30), "LISTA DE PRECIOS 📲", fill=(0, 102, 204), font=font_titulo)
    
    # Dibujar Línea separadora
    d.line((50, 110, 750, 110), fill=(200, 200, 200), width=3)

    # Dibujar la lista
    y_text = 130
    for linea in lineas:
        d.text((50, y_text), linea, fill=color_texto, font=font)
        y_text += alto_linea
    
    return img

# --- LÓGICA PRINCIPAL ---
if st.button("Generar Imagen 🖼️", type="primary"):
    if texto_entrada:
        # A. Calcular Precios (+50)
        def sumar_precio(match):
            return str(int(match.group()) + 50)
        
        texto_procesado = re.sub(r'\b\d{3,4}\b', sumar_precio, texto_entrada)

        # B. Generar la imagen
        imagen_final = crear_imagen(texto_procesado)
        
        # C. Mostrar la imagen en pantalla
        st.image(imagen_final, caption="Vista previa")

        # D. Convertir imagen a bytes para poder descargarla
        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # E. Botón de Descarga
        st.download_button(
            label="Descargar Imagen para WhatsApp 📥",
            data=byte_im,
            file_name="lista_precios.png",
            mime="image/png"
        )
    else:
        st.warning("Primero pega la lista arriba.")
