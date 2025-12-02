import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap  # <--- IMPORTANTE: Necesitamos esta librería estándar

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador iPhone", layout="centered")
st.title("🍏 Generador de Lista Automático")
st.markdown("Pega **toda la lista completa** abajo. El sistema calcula alturas y ajusta el texto largo automáticamente.")

# --- 1. FUNCIÓN DE LIMPIEZA Y CÁLCULO (+50) ---
def procesar_bloque(texto_crudo):
    if not texto_crudo:
        return ""
    def sumar_precio(match):
        precio_num = int(match.group(1))
        nuevo_precio = precio_num + 50
        return f"{nuevo_precio}$"
    texto_procesado = re.sub(r'(\d{3,4})\s?\$', sumar_precio, texto_crudo)
    return texto_procesado

# --- 2. INTERFAZ ---
texto_completo = st.text_area("Pega el listado completo aquí:", height=400)

# --- 3. LÓGICA DE SEPARACIÓN ---
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


# --- NUEVA FUNCIÓN AUXILIAR: ENVOLVER TEXTO LARGO ---
def wrap_text(text, font, max_width):
    """Corta una línea larga en varias líneas si excede el ancho máximo."""
    lines = []
    # Si la línea ya es corta, la devuelve tal cual
    if font.getlength(text) <= max_width:
        return [text]
    
    # Si es larga, usa textwrap para cortarla por palabras
    # Aproximamos cuántos caracteres entran en el ancho (es un cálculo estimado)
    avg_char_width = font.getlength("A") * 0.9 # Ajuste empírico
    max_chars = int(max_width / avg_char_width)
    wrapper = textwrap.TextWrapper(width=max_chars, break_long_words=False, replace_whitespace=False)
    lines = wrapper.wrap(text)
    return lines


# --- 4. MOTOR GRÁFICO ---
def crear_imagen(fecha, txt_sellados, txt_testers):
    W = 1080
    
    # Constantes
    ALTURA_HEADER = 300
    ALTO_BANNER = 85
    PADDING_CAJA = 30
    ALTO_LINEA = 55 # Espacio vertical entre renglones
    ESPACIO_ENTRE_BLOQUES = 50
    MARGIN_BOTTOM = 100
    MARGEN_X = 50
    ANCHO_UTIL_TEXTO = W - (MARGEN_X * 2) - 60 # Ancho disponible dentro de la caja blanca

    # Cargar Fuente (la necesitamos antes para calcular el wrap)
    try:
        font_lista = ImageFont.truetype("font.ttf", 40)
    except:
        font_lista = ImageFont.load_default()

    # --- PRE-PROCESAMIENTO: Envolver líneas largas y calcular altura real ---
    
    # Procesar Sellados
    lineas_finales_sellados = []
    if txt_sellados:
        for linea_cruda in txt_sellados.strip().split('\n'):
            # Usamos la nueva función para cortar si es larga
            lineas_envueltas = wrap_text(linea_cruda.strip(), font_lista, ANCHO_UTIL_TEXTO)
            lineas_finales_sellados.extend(lineas_envueltas)
            
    alto_bloque_sellados = 0
    if lineas_finales_sellados:
        # La altura depende de cuántas líneas finales quedaron después del wrap
        alto_caja_sellados = (len(lineas_finales_sellados) * ALTO_LINEA) + (PADDING_CAJA * 2)
        alto_bloque_sellados = ALTO_BANNER + alto_caja_sellados + ESPACIO_ENTRE_BLOQUES

    # Procesar Testers (Misma lógica)
    lineas_finales_testers = []
    if txt_testers:
        for linea_cruda in txt_testers.strip().split('\n'):
            lineas_envueltas = wrap_text(linea_cruda.strip(), font_lista, ANCHO_UTIL_TEXTO)
            lineas_finales_testers.extend(lineas_envueltas)

    alto_bloque_testers = 0
    if lineas_finales_testers:
        alto_caja_testers = (len(lineas_finales_testers) * ALTO_LINEA) + (PADDING_CAJA * 2)
        alto_bloque_testers = ALTO_BANNER + alto_caja_testers

    # Calcular Altura Total H
    H = ALTURA_HEADER + alto_bloque_sellados + alto_bloque_testers + MARGIN_BOTTOM
    H = max(H, 1000)

    # --- DIBUJAR ---
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fondo Degradado
    for y in range(H):
        r = int(65 + (190 * (y / H)))
        g = int(105 - (50 * (y / H)))
        b = 255
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Cargar resto de fuentes e imagen
    try:
        font_titulo = ImageFont.truetype("font.ttf", 100)
        font_sub = ImageFont.truetype("font.ttf", 50)
        font_banner = ImageFont.truetype("font.ttf", 45)
    except:
        font_titulo = font_sub = font_banner = ImageFont.load_default()

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

    # Dibujar Bloques
    cursor_y = ALTURA_HEADER
    ancho_caja_externo = W - (MARGEN_X * 2)

    # BLOQUE 1: SELLADOS
    if lineas_finales_sellados:
        # Banner
        draw.rectangle([(MARGEN_X, cursor_y), (MARGEN_X + 620, cursor_y + ALTO_BANNER)], fill=(106, 196, 168))
        draw.text((MARGEN_X + 25, cursor_y + 15), "■ IPHONES SELLADOS ■", font=font_banner, fill=(30, 30, 30))
        cursor_y += ALTO_BANNER
        # Caja
        alto_caja = (len(lineas_finales_sellados) * ALTO_LINEA) + (PADDING_CAJA * 2)
        draw.rectangle([(MARGEN_X, cursor_y), (MARGEN_X + ancho_caja_externo, cursor_y + alto_caja)], outline=(255, 255, 255), width=4)
        
        y_text = cursor_y + PADDING_CAJA
        # Usamos la lista ya procesada (envuelta)
        for linea in lineas_finales_sellados:
            draw.text((MARGEN_X + 30, y_text), linea, font=font_lista, fill=(255, 255, 255))
            y_text += ALTO_LINEA
        
        cursor_y += alto_caja + ESPACIO_ENTRE_BLOQUES

    # BLOQUE 2: TESTERS
    if lineas_finales_testers:
        # Banner
        draw.rectangle([(MARGEN_X, cursor_y), (MARGEN_X + 620, cursor_y + ALTO_BANNER)], fill=(227, 201, 57))
        draw.text((MARGEN_X + 25, cursor_y + 15), "■ IPHONE TESTERS ■", font=font_banner, fill=(30, 30, 30))
        cursor_y += ALTO_BANNER
        # Caja
        alto_caja = (len(lineas_finales_testers) * ALTO_LINEA) + (PADDING_CAJA * 2)
        draw.rectangle([(MARGEN_X, cursor_y), (MARGEN_X + ancho_caja_externo, cursor_y + alto_caja)], outline=(255, 255, 255), width=4)
        
        y_text = cursor_y + PADDING_CAJA
        # Usamos la lista ya procesada (envuelta)
        for linea in lineas_finales_testers:
            draw.text((MARGEN_X + 30, y_text), linea, font=font_lista, fill=(255, 255, 255))
            y_text += ALTO_LINEA

    return img

# --- 5. BOTÓN DE ACCIÓN ---
if st.button("GENERAR IMAGEN 🖼️", type="primary", use_container_width=True):
    if not texto_completo:
        st.warning("Pega la lista primero.")
    else:
        fecha_detectada, raw_sellados, raw_testers = separar_listas(texto_completo)
        sellados_listo = procesar_bloque(raw_sellados)
        testers_listo = procesar_bloque(raw_testers)
        imagen_final = crear_imagen(fecha_detectada, sellados_listo, testers_listo)
        
        # Mostrar imagen en la web (con ancho controlado para que no se vea gigante)
        st.image(imagen_final, caption="Vista Previa (El texto largo se ajustará)", width=500)

        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label="DESCARGAR IMAGEN 📥", data=byte_im, file_name="lista_iphone_ajustada.png", mime="image/png", use_container_width=True
        )
