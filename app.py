import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador iPhone", layout="centered")
st.title("🍏 Generador de Lista (Letras + Emojis)")
st.markdown("Ahora usando fuente **Híbrida** para que se vean textos y símbolos a la vez.")

# --- 1. PROCESAMIENTO ---
def procesar_bloque(texto_crudo):
    if not texto_crudo:
        return ""
    def sumar_precio(match):
        precio_num = int(match.group(1))
        nuevo_precio = precio_num + 50
        return f"{nuevo_precio}$"
    # Detecta precios y suma 50
    texto_procesado = re.sub(r'(\d{3,4})\s?\$', sumar_precio, texto_crudo)
    return texto_procesado

# --- 2. INTERFAZ ---
texto_completo = st.text_area("Pega el listado completo aquí:", height=400)

# --- 3. SEPARACIÓN ---
def separar_listas(texto):
    sellados = ""
    testers = ""
    fecha_extraida = ""
    texto_upper = texto.upper()
    
    idx_sellados = texto_upper.find("SELLADOS")
    idx_testers = texto_upper.find("TESTERS")

    if idx_sellados != -1:
        encabezado = texto[:idx_sellados]
        for linea in encabezado.split('\n'):
            if "Actualizada" in linea or "/" in linea:
                fecha_extraida = linea.replace("⬇", "").replace("Updating", "").strip()

    if idx_sellados != -1 and idx_testers != -1:
        inicio_sellados = idx_sellados + 8 
        fin_sellados = texto_upper.rfind("IPHONE", 0, idx_testers) 
        if fin_sellados == -1: fin_sellados = idx_testers
        sellados = texto[inicio_sellados:fin_sellados].strip()
        inicio_testers = idx_testers + 7
        testers = texto[inicio_testers:].strip()
        sellados = sellados.replace("◾", "").strip()
        testers = testers.replace("◼", "").strip()
    elif idx_sellados != -1:
        sellados = texto[idx_sellados+8:].strip()
    return fecha_extraida, sellados, testers

# --- WRAPPER (Corte de línea) ---
def wrap_text(text, font, max_width):
    if font.getlength(text) <= max_width:
        return [text]
    avg_char_width = font.getlength("A") * 0.95
    max_chars = int(max_width / avg_char_width)
    wrapper = textwrap.TextWrapper(width=max_chars, break_long_words=False, replace_whitespace=False)
    return wrapper.wrap(text)

# --- 4. MOTOR GRÁFICO ---
def crear_imagen(fecha, txt_sellados, txt_testers):
    W = 1080
    
    # Constantes
    ALTURA_HEADER = 300
    ALTO_BANNER = 90
    PADDING_CAJA = 35
    ALTO_LINEA = 55 
    ESPACIO_ENTRE_BLOQUES = 60
    MARGIN_BOTTOM = 100
    MARGEN_X = 50
    ANCHO_UTIL_TEXTO = W - (MARGEN_X * 2) - 70 

    # --- CARGA DE FUENTES ---
    # 1. Fuente bonita para Títulos (Si falla, usa default)
    try:
        font_titulo = ImageFont.truetype("font.ttf", 100)
        font_sub = ImageFont.truetype("font.ttf", 50)
        font_banner = ImageFont.truetype("font.ttf", 45)
    except:
        font_titulo = font_sub = font_banner = ImageFont.load_default()

    # 2. Fuente Híbrida para la Lista (Letras + Emojis)
    # IMPORTANTE: Aquí buscamos el archivo emoji.ttf nuevo que subiste
    try:
        font_lista = ImageFont.truetype("emoji.ttf", 40)
    except:
        # Si no lo encuentra, usa la font normal (se verán letras pero no emojis)
        try:
            font_lista = ImageFont.truetype("font.ttf", 40)
        except:
            font_lista = ImageFont.load_default()

    # --- PRE-PROCESAMIENTO ---
    lineas_finales_sellados = []
    if txt_sellados:
        for linea in txt_sellados.strip().split('\n'):
            lineas_envueltas = wrap_text(linea.strip(), font_lista, ANCHO_UTIL_TEXTO)
            lineas_finales_sellados.extend(lineas_envueltas)
            
    lineas_finales_testers = []
    if txt_testers:
        for linea in txt_testers.strip().split('\n'):
            lineas_envueltas = wrap_text(linea.strip(), font_lista, ANCHO_UTIL_TEXTO)
            lineas_finales_testers.extend(lineas_envueltas)

    # Calcular Alturas
    alto_bloque_sellados = 0
    if lineas_finales_sellados:
        alto_caja = (len(lineas_finales_sellados) * ALTO_LINEA) + (PADDING_CAJA * 2)
        alto_bloque_sellados = ALTO_BANNER + alto_caja + ESPACIO_ENTRE_BLOQUES

    alto_bloque_testers = 0
    if lineas_finales_testers:
        alto_caja = (len(lineas_finales_testers) * ALTO_LINEA) + (PADDING_CAJA * 2)
        alto_bloque_testers = ALTO_BANNER + alto_caja

    H = ALTURA_HEADER + alto_bloque_sellados + alto_bloque_testers + MARGIN_BOTTOM
    H = max(H, 1200)

    # --- DIBUJAR ---
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    for y in range(H):
        r = int(65 + (190 * (y / H)))
        g = int(105 - (50 * (y / H)))
        b = 255
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Imagen del iPhone
    try:
        top_img = Image.open("top_img.png").convert("RGB")
        baseheight = 250
        hpercent = (baseheight / float(top_img.size[1]))
        wsize = int((float(top_img.size[0]) * float(hpercent)))
        top_img = top_img.resize((wsize, baseheight))
        img.paste(top_img, (W - wsize, 0))
    except:
        pass

    # Títulos
    draw.text((50, 80), "IPHONE", font=font_titulo, fill=(255, 255, 255))
    texto_fecha = fecha if fecha else "LISTA DE PRECIOS ACTUALIZADA"
    draw.text((50, 200), texto_fecha, font=font_sub, fill=(255, 255, 255))

    cursor_y = ALTURA_HEADER
    ancho_caja_externo = W - (MARGEN_X * 2)

    # DIBUJO BLOQUES
    if lineas_finales_sellados:
        draw.rectangle([(MARGEN_X, cursor_y), (MARGEN_X + 620, cursor_y + ALTO_BANNER)], fill=(106, 196, 168))
        draw.text((MARGEN_X + 25, cursor_y + 20), "■ IPHONES SELLADOS ■", font=font_banner, fill=(30, 30, 30))
        cursor_y += ALTO_BANNER
        
        alto_caja = (len(lineas_finales_sellados) * ALTO_LINEA) + (PADDING_CAJA * 2)
        draw.rectangle([(MARGEN_X, cursor_y), (MARGEN_X + ancho_caja_externo, cursor_y + alto_caja)], outline=(255, 255, 255), width=4)
        
        y_text = cursor_y + PADDING_CAJA
        for linea in lineas_finales_sellados:
            # Aquí usamos la fuente híbrida (emoji.ttf)
            draw.text((MARGEN_X + 30, y_text), linea, font=font_lista, fill=(255, 255, 255))
            y_text += ALTO_LINEA
        
        cursor_y += alto_caja + ESPACIO_ENTRE_BLOQUES

    if lineas_finales_testers:
        draw.rectangle([(MARGEN_X, cursor_y), (MARGEN_X + 620, cursor_y + ALTO_BANNER)], fill=(227, 201, 57))
        draw.text((MARGEN_X + 25, cursor_y + 20), "■ IPHONE TESTERS ■", font=font_banner, fill=(30, 30, 30))
        cursor_y += ALTO_BANNER
        
        alto_caja = (len(lineas_finales_testers) * ALTO_LINEA) + (PADDING_CAJA * 2)
        draw.rectangle([(MARGEN_X, cursor_y), (MARGEN_X + ancho_caja_externo, cursor_y + alto_caja)], outline=(255, 255, 255), width=4)
        
        y_text = cursor_y + PADDING_CAJA
        for linea in lineas_finales_testers:
            draw.text((MARGEN_X + 30, y_text), linea, font=font_lista, fill=(255, 255, 255))
            y_text += ALTO_LINEA

    return img

# --- BOTÓN ---
if st.button("GENERAR IMAGEN 🖼️", type="primary", use_container_width=True):
    if not texto_completo:
        st.warning("Pega la lista primero.")
    else:
        fecha_detectada, raw_sellados, raw_testers = separar_listas(texto_completo)
        sellados_listo = procesar_bloque(raw_sellados)
        testers_listo = procesar_bloque(raw_testers)
        imagen_final = crear_imagen(fecha_detectada, sellados_listo, testers_listo)
        
        st.image(imagen_final, caption="Vista Previa", width=500)

        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(label="DESCARGAR IMAGEN 📥", data=byte_im, file_name="lista_iphone_ok.png", mime="image/png", use_container_width=True)
