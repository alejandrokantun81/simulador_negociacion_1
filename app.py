import streamlit as st
import google.generativeai as genai
import time
import streamlit.components.v1 as components
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador Maderas Globales - Acceso Corporativo",
    page_icon="🔐",
    layout="wide"
)

# --- 2. SISTEMA DE AUTENTICACIÓN (LOGIN) ---
def check_password():
    """Retorna True si el usuario ingresó credenciales correctas."""
    
    # DEFINA AQUÍ SUS USUARIOS Y CONTRASEÑAS
    credenciales_validas = {
        "admin": "admin123",      # Para usted
        "cobay": "clase2025",     # Para sus alumnos
        "demo": "prueba1",        # Para clientes potenciales
        "cliente_vip": "maderas"  # Ejemplo comercial
    }
    
    # Verificar si ya inició sesión
    if st.session_state.get("logged_in", False):
        return True
    
    # Interfaz de Login
    st.header("🔐 Acceso al Simulador de Negociación")
    st.markdown("Este es un entorno de entrenamiento privado. Por favor identifíquese.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", type="primary"):
            if usuario in credenciales_validas and credenciales_validas[usuario] == password:
                st.session_state.logged_in = True
                st.success("Acceso concedido...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Contacte al administrador.")
    
    return False

# SI NO ESTÁ LOGUEADO, DETENER EL CÓDIGO AQUÍ
if not check_password():
    st.stop()

# ==========================================
#      A PARTIR DE AQUÍ: EL SIMULADOR
#      (Solo se ejecuta si check_password es True)
# ==========================================

# --- 3. LÓGICA DE VÍCTOR KOVACS ---
def obtener_instruccion_sistema(turno_actual, nombre_alumno):
    contexto = f"""
    ROL: Sr. Víctor Kovacs, Director Comercial de 'Maderas Globales'.
    USUARIO: {nombre_alumno}.
    PERSONALIDAD: Arrogante, impaciente, pragmático.
    ESTILO: Frases cortas. Interrumpe. Usa el nombre '{nombre_alumno}' para presionar.
    """
    
    comportamiento_turno = ""
    
    if turno_actual <= 2:
        comportamiento_turno = f"FASE DE APERTURA (Turno {turno_actual}): Saluda a {nombre_alumno} con frialdad. Rechaza su propuesta. Exige el 25%."
    elif turno_actual == 3:
        comportamiento_turno = "FASE DE EVIDENCIA (Turno 3): INSTRUCCIÓN OBLIGATORIA: Di 'Mira los números tú mismo' y coloca la etiqueta <GRAFICA_INVENTARIO>."
    elif turno_actual == 4:
        comportamiento_turno = "FASE DE DRAMA (Turno 4): INSTRUCCIÓN OBLIGATORIA: Di 'Escucha a mi financiero' y coloca la etiqueta <AUDIO_CONFIDENCIAL>."
    elif 5 <= turno_actual <= 7:
        comportamiento_turno = "FASE DE NEGOCIACIÓN: Ya mostraste tus cartas. Si ofrecen Pago Inmediato (A) o Doble Volumen (B), acepta. Si no, presiona."
    elif 8 <= turno_actual <= 9:
        comportamiento_turno = "FASE FINAL: Di 'Tengo otra llamada'. Cierra o cuelga."
    else:
        comportamiento_turno = "FIN DEL JUEGO: 'Se acabó el tiempo'. Cuelga."

    condiciones_victoria = """
    CONDICIONES PARA ACEPTAR:
    A) 15% aumento + PAGO INMEDIATO -> Acepta ("Trato hecho").
    B) 12% aumento + DOBLE VOLUMEN -> Acepta ("Trato hecho").
    SI NO: Rechaza.
    """
    return f"{contexto}\n\nTURNO ACTUAL: {turno_actual}/10\nORDEN: {comportamiento_turno}\n{condiciones_victoria}"

# --- 4. BARRA LATERAL ---
with st.sidebar:
    # Botón de Logout (Nuevo)
    if st.button("Cerrar Sesión 🔒"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.divider()
    st.header("⚙️ Configuración")
    st.info("Caso: Maderas Globales")
    
    nombre_alumno = st.text_input("Nombre del Participante")
    
    if st.button("Llamar al Sr. Kovacs 📞", type="primary"):
        if not nombre_alumno:
            st.error("Escribe tu nombre.")
        else:
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                st.session_state.start_time = time.time()
                st.session_state.active = True
                st.session_state.messages = []
                st.session_state.turnos = 1
                st.session_state.nombre_alumno = nombre_alumno
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-flash-latest')
                st.session_state.chat = model.start_chat(history=[])
                
                initial_msg = f"Maderas Globales, habla Kovacs. {nombre_alumno}, tengo 2 minutos. ¿Para qué llama?"
                st.session_state.messages.append({"role": "model", "content": initial_msg})
                st.session_state.chat.history.append({"role": "model", "parts": [initial_msg]})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# --- 5. ZONA PRINCIPAL ---
st.title("Simulador de Negociación Corporativa 🌲")

if "active" not in st.session_state:
    st.session_state.active = False
if "turnos" not in st.session_state:
    st.session_state.turnos = 1

if st.session_state.active:
    elapsed = time.time() - st.session_state.start_time
    remaining = 600 - elapsed
    
    if remaining <= 0 or st.session_state.turnos > 10:
        st.session_state.active = False
        st.error("📞 SE CORTÓ LA LLAMADA.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1: st.metric("Turnos", f"{st.session_state.turnos}/10")
    with col2:
        components.html(f"""
        <div style="text-align:right; color:#555; font-family:sans-serif;">
            TIEMPO: <span style="color:#ff4b4b; font-weight:bold; font-size:1.5rem;">{int(remaining)//60:02d}:{int(remaining)%60:02d}</span>
        </div>
        """, height=50)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("has_chart"):
                st.caption("📉 ANEXO: Reporte de Almacén")
                chart_data = pd.DataFrame({"Mes": ["Ene", "Feb", "Mar", "Abr", "May"], "Ocupación (%)": [65, 72, 85, 93, 99]})
                st.bar_chart(chart_data.set_index("Mes"), color="#ff4b4b")
            if msg.get("has_audio"):
                st.info("▶️ **Nota de Voz (12s)**")
                st.markdown("> *Audio: 'Víctor, el banco rechazó la prórroga. Necesitamos cash flow YA.'*")

    if prompt := st.chat_input("Escribe tu respuesta..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        instruccion = obtener_instruccion_sistema(st.session_state.turnos, st.session_state.nombre_alumno)
        prompt_final = f"{prompt} \n\n[SISTEMA: {instruccion}]"
        
        try:
            response = st.session_state.chat.send_message(prompt_final)
            bot_reply = response.text
            
            has_chart = "<GRAFICA_INVENTARIO>" in bot_reply
            has_audio = "<AUDIO_CONFIDENCIAL>" in bot_reply
bot_reply = bot_reply.replace("<GRAFICA_INVENTARIO>", "").replace("<AUDIO_CONFIDENCIAL>", "").strip()

