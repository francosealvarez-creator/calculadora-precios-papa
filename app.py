import streamlit as st
import re
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Generador iPhone", layout="centered")
st.title("🍏 Generador de Lista Automático")
st.markdown("Pega **toda la lista completa** abajo. El sistema separa Sellados y Testers, suma +50 USD y genera la imagen.")

# --- 1. FUNCIÓN DE LIMPIEZA Y CÁLCULO (+50) ---
def procesar_bloque(texto_crudo):
    if not texto_crudo:
        return ""
    
    def sumar_precio(match):
        # Grupo 1 es el número. Lo convertimos, sumamos 50.
        precio_num = int(match.group(1))
        nuevo_precio = precio_num + 50
        # Devolvemos el número nuevo + el signo $
        return f"{nuevo_precio}$"
    
    # Regex: Busca números de 3 dígitos (ej: 480) seguidos opcionalmente de espacio y un signo $
    # Ejemplo: detecta "480$" o "480 $"
    texto_procesado = re.sub(r'(\d{3,4})\s?\$', sumar_precio, texto_crudo)
    return texto_procesado

# --- 2. INTERFAZ: UNA SOLA CAJA ---
texto_completo = st.text_area("Pega el listado completo de WhatsApp aquí:", height=400)

# --- 3. LÓGICA DE SEPARACIÓN AUTOMÁTICA ---
def separar_listas(texto):
    sellados = ""
    testers = ""
    fecha_extraida = ""

    # Normalizamos a mayúsculas para buscar palabras clave
    texto_upper = texto.upper()
    
    # Índices de corte
    idx_sellados = texto_upper.find("SELLADOS")
    idx_testers = texto_upper.find("TESTERS")

    # 1. Intentar sacar la fecha del encabezado (lo que está antes de "SELLADOS")
    if idx_sellados != -1:
        encabezado = texto[:idx_sellados]
        # Buscar algo que parezca fecha tipo "2/12" o "Lista Actualizada"
        lineas_header = encabezado.split('\n')
        for linea in lineas_header:
            if "Actualizada" in linea or "/" in linea:
                fecha_extraida = linea.replace("⬇", "").strip() # Limpieza básica

    # 2. Cortar el texto
    if idx_sellados != -1 and idx_testers != -1:
        # CASO IDEAL: Están las dos secciones
        # Sellados: Desde que termina la palabra "SELLADOS" hasta donde empieza "IPHONE TESTERS"
        # El +8 es para saltar la palabra "SELLADOS" y los caracteres raros (■)
        inicio_sellados = idx_sellados + 8 
        # Ajustamos el final restando unos caracteres para no agarrar el título "IPHONE" de abajo
        fin_sellados = texto_upper.rfind("IPHONE", 0, idx_testers) 
        if fin_sellados == -1: fin_sellados = idx_testers # Si falla, corta directo en TESTERS
        
        sellados = texto[inicio_sellados:fin_sellados].strip()
        
        # Testers: Desde que termina "TESTERS" hasta el final
        inicio_testers = idx_testers + 7
        testers = texto[inicio_testers:].strip()
        
        # Limpieza extra: Quitar los caracteres de adorno del inicio de cada bloque si quedaron
        sellados = sellados.replace("◾", "").strip()
        testers = testers.replace("◼", "").strip()

    elif idx_sellados != -1:
        # Solo hay sellados
        sellados = texto[idx_sellados+8:].strip()
    
    return fecha_extraida, sellados, testers


# --- 4. MOTOR GRÁFICO ---
def crear_imagen(fecha, txt_sellados, txt_testers):
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # A. Fondo Degradado
    for y in range(H):
        r = int(65 + (190 * (y / H)))
        g = int(105 - (50 * (y / H)))
        b = 255
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # B. Cargar Fuente e Imagen
    try:
        font_titulo = ImageFont.truetype("font.ttf", 100)
        font_sub = ImageFont.truetype("font.ttf", 50)
        font_banner = ImageFont.truetype("font.ttf", 45)
        font_lista = ImageFont.truetype("font.ttf", 40) # Fuente para la lista
    except:
        font_titulo = font_sub = font_banner = font_lista = ImageFont.load_default()

    try:
        # Cargar PNG y convertir a RGB
        top_img = Image.open("top_img.png").convert("RGB")
        
        # --- CAMBIO: Imagen más chica ---
        # Ahora forzamos que mida 250px de alto (antes era 400)
        baseheight = 250
        hpercent = (baseheight / float(top_img.size[1]))
        wsize = int((float(top_img.size[0]) * float(hpercent)))
        top_img = top_img.resize((wsize, baseheight))
        img.paste(top_img, (W - wsize, 0))
    except:
        pass

    # C. Títulos
    draw.text((50, 80), "IPHONE", font=font_titulo, fill=(255, 255, 255))
    
    texto_fecha = fecha if fecha else "LISTA DE PRECIOS ACTUALIZADA"
    draw.text((50, 200), texto_fecha, font=font_sub, fill=(255, 255, 255))

    # D. Dibujar Bloques
    cursor_y = 300
    margen_x = 50
    ancho_util = W - (margen_x * 2)
    padding_caja = 30

    # BLOQUE 1: SELLADOS
    if txt_sellados:
        # Banner Verde
        draw.rectangle([(margen_x, cursor_y), (margen_x + 620, cursor_y + 80)], fill=(106, 196, 168))
        draw.text((margen_x + 25, cursor_y + 15), "■ IPHONES SELLADOS ■", font=font_banner, fill=(30, 30, 30))
        cursor_y += 85

        # Caja Blanca
        lineas = txt_sellados.split('\n')
        alto_caja = (len(lineas) * 55) + (padding_caja * 2)
        
        draw.rectangle([(margen_x, cursor_y), (margen_x + ancho_util, cursor_y + alto_caja)], outline=(255, 255, 255), width=4)
        
        y_text = cursor_y + padding_caja
        for linea in lineas:
            # Limpieza ligera de emojis rotos si es necesario, o se dibujan tal cual
            linea_limpia = linea.strip() 
            draw.text((margen_x + 30, y_text), linea_limpia, font=font_lista, fill=(255, 255, 255))
            y_text += 55
        
        cursor_y += alto_caja + 50

    # BLOQUE 2: TESTERS
    if txt_testers:
        # Banner Amarillo
        draw.rectangle([(margen_x, cursor_y), (margen_x + 620, cursor_y + 80)], fill=(227, 201, 57))
        draw.text((margen_x + 25, cursor_y + 15), "■ IPHONE TESTERS ■", font=font_banner, fill=(30, 30, 30))
        cursor_y += 85

        # Caja Blanca
        lineas = txt_testers.split('\n')
        alto_caja = (len(lineas) * 55) + (padding_caja * 2)
        
        draw.rectangle([(margen_x, cursor_y), (margen_x + ancho_util, cursor_y + alto_caja)], outline=(255, 255, 255), width=4)
        
        y_text = cursor_y + padding_caja
        for linea in lineas:
            linea_limpia = linea.strip()
            draw.text((margen_x + 30, y_text), linea_limpia, font=font_lista, fill=(255, 255, 255))
            y_text += 55

    return img

# --- 5. BOTÓN DE ACCIÓN ---
if st.button("GENERAR IMAGEN 🖼️", type="primary", use_container_width=True):
    if not texto_completo:
        st.warning("Pega la lista primero.")
    else:
        # 1. Separar el texto crudo
        fecha_detectada, raw_sellados, raw_testers = separar_listas(texto_completo)
        
        # 2. Calcular precios (+50) en cada parte
        sellados_listo = procesar_bloque(raw_sellados)
        testers_listo = procesar_bloque(raw_testers)

        # 3. Generar imagen
        imagen_final = crear_imagen(fecha_detectada, sellados_listo, testers_listo)

        st.image(imagen_final, caption="Vista Previa", use_container_width=True)

        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="DESCARGAR IMAGEN 📥",
            data=byte_im,
            file_name="lista_iphone_ok.png",
            mime="image/png",
            use_container_width=True
        )
