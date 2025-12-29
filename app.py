import streamlit as st
import google.generativeai as genai
import time
import streamlit.components.v1 as components
import pandas as pd # Necesario para las gráficas

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Negociación - Caso Maderas Globales",
    page_icon="🌲",
    layout="wide"
)

# --- 2. EL CEREBRO DE VÍCTOR KOVACS (LÓGICA DINÁMICA) ---
def obtener_instruccion_sistema(turno_actual, nombre_alumno):
    """
    Genera el prompt dinámico con nombre y triggers multimedia.
    """
    # Definición del Escenario
    contexto = f"""
    ROL: Eres el Sr. Víctor Kovacs, Director Comercial de 'Maderas Globales'.
    USUARIO: Estás hablando con {nombre_alumno}.
    PERSONALIDAD: Arrogante, impaciente, pragmático y dominante.
    ESTILO: Usa frases cortas. Interrumpe. Menciona el nombre del usuario ({nombre_alumno}) para presionar, por ejemplo: "Mira, {nombre_alumno}, no tengo tiempo para esto".
    
    CONTEXTO OCULTO (TUS PROBLEMAS REALES):
    1. Crisis de Liquidez: Necesitas efectivo YA.
    2. Saturación de Almacén: Tienes el almacén al 98% de capacidad (costos de almacenaje brutales).
    
    HERRAMIENTAS MULTIMEDIA (ÚSALAS ESTRATÉGICAMENTE):
    - Si estás en el Turno 4, 5 o 6 y quieres probar que tu almacén va a explotar, escribe EXACTAMENTE al final de tu frase: <GRAFICA_INVENTARIO>
    - Si quieres dar un detalle confidencial sobre tus deudas, escribe EXACTAMENTE: <AUDIO_CONFIDENCIAL>
    """
    
    # Dinámica de Turnos
    comportamiento_turno = ""
    if turno_actual <= 3:
        comportamiento_turno = "FASE HOSTIL (Turnos 1-3): Rechaza todo. Exige el 25% de aumento. Sé duro con el nombre del usuario."
    elif 4 <= turno_actual <= 7:
        comportamiento_turno = "FASE DE EVIDENCIA (Turnos 4-7): Si el usuario duda, usa la etiqueta <GRAFICA_INVENTARIO> para mostrarle que no mientes sobre el stock. O usa <AUDIO_CONFIDENCIAL> para filtrar que el banco te está presionando."
    elif 8 <= turno_actual <= 9:
        comportamiento_turno = "FASE DE PRESIÓN (Turnos 8-9): Di 'Tengo otra llamada entrando'. Exige cierre inmediato."
    else:
        comportamiento_turno = "FASE FINAL (Turno 10): Si no hay acuerdo, cuelga."

    # Condiciones de Victoria
    condiciones_victoria = """
    CONDICIONES PARA ACEPTAR (SOLO SI CUMPLEN A o B):
    
    OPCIÓN A (Financiera): Aceptas 15% de aumento SI hay PAGO INMEDIATO o ADELANTO 50%.
    OPCIÓN B (Logística): Aceptas 12% de aumento SI hay DOBLE VOLUMEN o RETIRO INMEDIATO.
    
    SI NO, RECHAZA. Si aceptan, di: "Trato hecho".
    """
    
    return f"{contexto}\n\nTURNO ACTUAL: {turno_actual}/10\nINSTRUCCIÓN: {comportamiento_turno}\n{condiciones_victoria}"

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Caso: Maderas Globales")
    
    # Capturamos el nombre para pasarlo a la IA
    nombre_alumno = st.text_input("Nombre del Alumno", value="Colega")
    
    if st.button("Llamar al Sr. Kovacs 📞", type="primary"):
        if not nombre_alumno:
            st.error("Por favor escribe tu nombre.")
        else:
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                st.session_state.start_time = time.time()
                st.session_state.active = True
                st.session_state.messages = []
                st.session_state.turnos = 1
                st.session_state.nombre_alumno = nombre_alumno # Guardamos el nombre
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-flash-latest')
                
                st.session_state.chat = model.start_chat(history=[])
                
                initial_msg = f"Maderas Globales, habla Kovacs. {nombre_alumno}, tengo 2 minutos. ¿Para qué llama? Espero que sea para aceptar el aumento del 25%."
                st.session_state.messages.append({"role": "model", "content": initial_msg})
                st.session_state.chat.history.append({"role": "model", "parts": [initial_msg]})
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- 4. ZONA PRINCIPAL ---
st.title("Simulador de Negociación: Maderas Globales 🌲")

if "active" not in st.session_state:
    st.session_state.active = False
if "turnos" not in st.session_state:
    st.session_state.turnos = 1

if st.session_state.active:
    # Reloj y Turnos
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

    # --- CHAT CON MULTIMEDIA ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # 🖼️ RENDERIZADO DE GRÁFICAS (Si el mensaje histórico tenía la etiqueta)
            if msg.get("has_chart"):
                st.caption("📎 Archivo adjunto: 'Niveles_Almacen_2025.png'")
                # Datos simulados de saturación
                chart_data = pd.DataFrame({
                    "Mes": ["Ene", "Feb", "Mar", "Abr", "May (Proy)"],
                    "Ocupación (%)": [65, 70, 85, 92, 99]
                })
                st.bar_chart(chart_data.set_index("Mes"), color="#ff4b4b")
            
            # 🔊 RENDERIZADO DE AUDIO (Si el mensaje histórico tenía la etiqueta)
            if msg.get("has_audio"):
                st.info("▶️ **Nota de Voz recibida (15s)**")
                st.markdown("*Transcripción automática: '...mira, el banco me está respirando en la nuca. Si no líquido stock antes del viernes, me ejecutan la garantía. Necesito el efectivo ya...'*")

    if prompt := st.chat_input("Escribe tu respuesta..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Inyección de contexto actualizada con el nombre
        instruccion = obtener_instruccion_sistema(st.session_state.turnos, st.session_state.nombre_alumno)
        prompt_final = f"{prompt} \n\n[SISTEMA: {instruccion}]"
        
        bot_reply = None
        try:
            response = st.session_state.chat.send_message(prompt_final)
            bot_reply = response.text
        except Exception as e:
            st.error(f"Error: {e}")

        if bot_reply:
            # --- DETECCIÓN DE TRIGGERS MULTIMEDIA ---
            has_chart = False
            has_audio = False
            
            # Limpiamos el texto de las etiquetas para que no se vean feas, pero activamos las banderas
            if "<GRAFICA_INVENTARIO>" in bot_reply:
                has_chart = True
                bot_reply = bot_reply.replace("<GRAFICA_INVENTARIO>", "").strip()
                
            if "<AUDIO_CONFIDENCIAL>" in bot_reply:
                has_audio = True
                bot_reply = bot_reply.replace("<AUDIO_CONFIDENCIAL>", "").strip()

            # Guardamos mensaje y banderas
            st.session_state.messages.append({
                "role": "model", 
                "content": bot_reply, 
                "has_chart": has_chart,
                "has_audio": has_audio
            })
            
            st.session_state.turnos += 1
            
            if "Trato hecho" in bot_reply:
                st.balloons()
                st.success(f"🏆 ¡TRATO CERRADO, {st.session_state.nombre_alumno.upper()}!")
                st.session_state.active = False
            else:
                st.rerun()

else:
    st.info("👈 Ingresa tu nombre para comenzar la simulación.")
