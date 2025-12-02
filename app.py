import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="Generador Lista iPhone", layout="centered")
st.title("🍏 Generador de Lista con Diseño")
st.markdown("Pega las listas abajo, el sistema suma **+50 USD** a todo y genera el diseño.")

# --- 1. FUNCIÓN MATEMÁTICA (SUMAR 50) ---
def procesar_texto_sumar_50(texto_crudo):
    if not texto_crudo:
        return ""
    
    def sumar_precio(match):
        # Toma el número encontrado, suma 50 y lo devuelve como texto
        return str(int(match.group()) + 50)
    
    # Busca números de 3 o 4 cifras (ej: 450, 1200) para no sumar al "14" de iPhone 14
    texto_procesado = re.sub(r'\b\d{3,4}\b', sumar_precio, texto_crudo)
    return texto_procesado

# --- 2. INTERFAZ PARA PEGAR TEXTO ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Listado SELLADOS")
    texto_sellados_input = st.text_area("Pega los sellados aquí:", height=300, key="sellados")
with col2:
    st.subheader("Listado TESTERS")
    texto_testers_input = st.text_area("Pega los testers aquí:", height=300, key="testers")

# --- 3. MOTOR GRÁFICO (DIBUJAR LA IMAGEN) ---
def crear_imagen_diseno_pro(texto_sellados, texto_testers):
    # A. Crear Lienzo (Tamaño Historia Instagram: 1080x1920)
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # B. Fondo Degradado (Azul a Rosa/Violeta)
    for y in range(H):
        r = int(65 + (190 * (y / H)))   # De azul oscuro a rosa brillante
        g = int(105 - (50 * (y / H)))   # Ajuste de verde
        b = 255                         # Mantener azul alto
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # C. Cargar Fuente (Tipografía)
    try:
        # Tamaños de letra
        font_titulo = ImageFont.truetype("font.ttf", 100)
        font_sub = ImageFont.truetype("font.ttf", 50)
        font_banner = ImageFont.truetype("font.ttf", 45)
        font_lista = ImageFont.truetype("font.ttf", 40)
    except:
        # Si falla, usar la por defecto (fea pero funciona)
        font_titulo = font_sub = font_banner = font_lista = ImageFont.load_default()

    # D. Cargar Imagen PNG (Esquina derecha)
    try:
        # --- CAMBIO AQUÍ: Ahora busca .png y lo convierte a RGB para evitar errores ---
        top_img = Image.open("top_img.png").convert("RGB")
        
        # Redimensionar para que tenga 400px de alto proporcionalmente
        baseheight = 400
        hpercent = (baseheight / float(top_img.size[1]))
        wsize = int((float(top_img.size[0]) * float(hpercent)))
        top_img = top_img.resize((wsize, baseheight))
        
        # Pegar en la esquina derecha
        img.paste(top_img, (W - wsize, 0))
    except Exception as e:
        print(f"No se pudo cargar la imagen PNG: {e}")
        pass # Si falla, sigue sin la imagen

    # E. Dibujar Títulos Principales
    draw.text((50, 100), "IPHONE", font=font_titulo, fill=(255, 255, 255))
    draw.text((50, 220), "LISTA DE PRECIOS ACTUALIZADA", font=font_sub, fill=(255, 255, 255))

    # F. Dibujar las Cajas de Precios
    cursor_y = 380 # Altura donde empieza el primer banner
    margen_x = 50
    ancho_util = W - (margen_x * 2)
    padding_caja = 35

    # --- BLOQUE 1: SELLADOS (VERDE) ---
    if texto_sellados:
        # 1. Banner Verde
        draw.rectangle([(margen_x, cursor_y), (margen_x + 620, cursor_y + 80)], fill=(106, 196, 168))
        draw.text((margen_x + 25, cursor_y + 15), "■ IPHONES SELLADOS ■", font=font_banner, fill=(30, 30, 30))
        cursor_y += 90 # Bajamos el cursor

        # 2. Caja Blanca (Borde)
        lineas = texto_sellados.strip().split('\n')
        # Calcular altura dinámica de la caja
        alto_caja = (len(lineas) * 55) + (padding_caja * 2)
        
        draw.rectangle([(margen_x, cursor_y), (margen_x + ancho_util, cursor_y + alto_caja)], outline=(255, 255, 255), width=5)
        
        # Escribir texto adentro
        y_texto = cursor_y + padding_caja
        for linea in lineas:
            draw.text((margen_x + 40, y_texto), linea, font=font_lista, fill=(255, 255, 255))
            y_texto += 55
        
        cursor_y += alto_caja + 60 # Espacio antes del siguiente bloque

    # --- BLOQUE 2: TESTERS (AMARILLO) ---
    if texto_testers:
        # 1. Banner Amarillo
        draw.rectangle([(margen_x, cursor_y), (margen_x + 620, cursor_y + 80)], fill=(227, 201, 57))
        draw.text((margen_x + 25, cursor_y + 15), "■ IPHONE TESTERS ■", font=font_banner, fill=(30, 30, 30))
        cursor_y += 90

        # 2. Caja Blanca
        lineas = texto_testers.strip().split('\n')
        alto_caja = (len(lineas) * 55) + (padding_caja * 2)
        
        draw.rectangle([(margen_x, cursor_y), (margen_x + ancho_util, cursor_y + alto_caja)], outline=(255, 255, 255), width=5)
        
        y_texto = cursor_y + padding_caja
        for linea in lineas:
            draw.text((margen_x + 40, y_texto), linea, font=font_lista, fill=(255, 255, 255))
            y_texto += 55

    return img

# --- 4. BOTÓN DE ACCIÓN ---
st.divider()
if st.button("GENERAR IMAGEN FINAL 🖼️", type="primary", use_container_width=True):
    if not texto_sellados_input and not texto_testers_input:
        st.warning("⚠️ Pega al menos una lista para empezar.")
    else:
        with st.spinner("Calculando precios y dibujando..."):
            # Calcular precios
            sellados_calc = procesar_texto_sumar_50(texto_sellados_input)
            testers_calc = procesar_texto_sumar_50(texto_testers_input)

            # Generar imagen
            imagen_final = crear_imagen_diseno_pro(sellados_calc, testers_calc)

            # Mostrar en pantalla (reducida para vista previa)
            st.success("¡Imagen generada! Revisa la vista previa y descárgala abajo.")
            st.image(imagen_final, caption="Vista Previa", use_container_width=True)

            # Botón Descargar (Calidad total)
            buf = io.BytesIO()
            imagen_final.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="DESCARGAR IMAGEN PARA WHATSAPP 📥",
                data=byte_im,
                file_name="lista_iphone_diseno.png",
                mime="image/png",
                use_container_width=True
            )
