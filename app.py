import streamlit as st
import google.generativeai as genai
import time
import streamlit.components.v1 as components
import pandas as pd

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Negociación - Caso Maderas Globales",
    page_icon="🌲",
    layout="wide"
)

# --- 2. EL CEREBRO DE VÍCTOR KOVACS (GUIÓN ESTRICTO) ---
def obtener_instruccion_sistema(turno_actual, nombre_alumno):
    """
    Genera el prompt con triggers OBLIGATORIOS para Gráfica y Audio.
    """
    # Escenario Base
    contexto = f"""
    ROL: Sr. Víctor Kovacs, Director Comercial de 'Maderas Globales'.
    USUARIO: {nombre_alumno}.
    PERSONALIDAD: Arrogante, impaciente, pragmático.
    ESTILO: Frases cortas. Interrumpe. Usa el nombre '{nombre_alumno}' para presionar.
    """
    
    # --- LÓGICA DE GUIÓN (SCRIPTING) ---
    comportamiento_turno = ""
    
    if turno_actual <= 2:
        comportamiento_turno = f"FASE DE APERTURA (Turno {turno_actual}): Saluda a {nombre_alumno} con frialdad. Rechaza su propuesta inicial con desprecio. Exige el 25% de aumento."
        
    elif turno_actual == 3:
        # --- TRIGGER OBLIGATORIO DE GRÁFICA ---
        comportamiento_turno = "FASE DE EVIDENCIA (Turno 3): El usuario no entiende. INSTRUCCIÓN OBLIGATORIA: Di 'Mira los números tú mismo, no tengo espacio' y coloca la etiqueta <GRAFICA_INVENTARIO> al final."
        
    elif turno_actual == 4:
        # --- TRIGGER OBLIGATORIO DE AUDIO ---
        comportamiento_turno = "FASE DE DRAMA (Turno 4): El banco presiona. INSTRUCCIÓN OBLIGATORIA: Di 'Escucha lo que me acaba de mandar mi financiero' y coloca la etiqueta <AUDIO_CONFIDENCIAL> al final."
        
    elif 5 <= turno_actual <= 7:
        comportamiento_turno = "FASE DE NEGOCIACIÓN: Ya mostraste tus cartas (saturación y deudas). Si ofrecen Pago Inmediato (Opción A) o Doble Volumen (Opción B), acepta. Si no, presiona con el tiempo."
        
    elif 8 <= turno_actual <= 9:
        comportamiento_turno = "FASE FINAL: Di 'Tengo otra llamada entrando'. Exige cierre inmediato o cuelgas."
        
    else:
        comportamiento_turno = "FIN DEL JUEGO: Si no hay acuerdo exacto ya, di 'Se acabó el tiempo' y cuelga."

    # Condiciones de Victoria
    condiciones_victoria = """
    CONDICIONES PARA ACEPTAR EL TRATO:
    OPCIÓN A (Financiera): 15% aumento + PAGO INMEDIATO/CONTADO -> Acepta ("Trato hecho").
    OPCIÓN B (Logística): 12% aumento + DOBLE VOLUMEN/RETIRO YA -> Acepta ("Trato hecho").
    
    SI NO CUMPLEN: Rechaza.
    """
    
    return f"{contexto}\n\nTURNO ACTUAL: {turno_actual}/10\nORDEN PARA ESTE TURNO: {comportamiento_turno}\n{condiciones_victoria}"

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Caso: Maderas Globales")
    
    # Capturamos el nombre
    nombre_alumno = st.text_input("Nombre del Alumno")
    
    if st.button("Llamar al Sr. Kovacs 📞", type="primary"):
        if not nombre_alumno:
            st.error("Por favor escribe tu nombre para iniciar.")
        else:
            try:
                # Opción A: Llave Institucional
                api_key = st.secrets["GOOGLE_API_KEY"]
                
                # Inicializar Sesión
                st.session_state.start_time = time.time()
                st.session_state.active = True
                st.session_state.messages = []
                st.session_state.turnos = 1
                st.session_state.nombre_alumno = nombre_alumno
                
                genai.configure(api_key=api_key)
                
                # MODELO VALIDADO
                model = genai.GenerativeModel('gemini-flash-latest')
                
                st.session_state.chat = model.start_chat(history=[])
                
                # Mensaje Inicial
                initial_msg = f"Maderas Globales, habla Kovacs. {nombre_alumno}, tengo 2 minutos. ¿Para qué llama? Espero que sea para aceptar el aumento del 25%."
                st.session_state.messages.append({"role": "model", "content": initial_msg})
                st.session_state.chat.history.append({"role": "model", "parts": [initial_msg]})
                st.rerun()
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- 4. ZONA PRINCIPAL ---
st.title("Simulador de Negociación: Maderas Globales 🌲")

if "active" not in st.session_state:
    st.session_state.active = False
if "turnos" not in st.session_state:
    st.session_state.turnos = 1

if st.session_state.active:
    # Lógica de Tiempo
    elapsed = time.time() - st.session_state.start_time
    remaining = 600 - elapsed
    
    # Check de Finalización
    if remaining <= 0 or st.session_state.turnos > 10:
        st.session_state.active = False
        st.error("📞 SE CORTÓ LA LLAMADA.")
        st.stop()

    # Panel Superior (Turnos y Reloj)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Turnos Utilizados", f"{st.session_state.turnos}/10")
    with col2:
        components.html(f"""
        <div style="text-align:right; color:#555; font-family:sans-serif;">
            TIEMPO: <span id="cnt" style="color:#ff4b4b; font-weight:bold; font-size:1.5rem;">--:--</span>
        </div>
        <script>
            var t = {int(remaining)};
            var e = document.getElementById("cnt");
            var x = setInterval(function() {{
                if(t<=0){{clearInterval(x);e.innerHTML="00:00";}}
                else{{
                    var m=Math.floor(t/60), s=t%60;
                    e.innerHTML=(m<10?"0"+m:m)+":"+(s<10?"0"+s:s);
                }}
                t-=1;
            }},1000);
        </script>
        """, height=50)

    # --- CHAT LOOP ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # 📊 RENDERIZADO DE GRÁFICA
            if msg.get("has_chart"):
                st.caption("📉 ANEXO: Reporte de Saturación de Almacén - Tiempo Real")
                # Datos simulados: Almacén llenándose peligrosamente
                chart_data = pd.DataFrame({
                    "Mes": ["Ene", "Feb", "Mar", "Abr", "May (Actual)"],
                    "Ocupación (%)": [65, 72, 85, 93, 99]
                })
                st.bar_chart(chart_data.set_index("Mes"), color="#ff4b4b")
            
            # 🔊 RENDERIZADO DE AUDIO
            if msg.get("has_audio"):
                st.info("▶️ **Nota de Voz Reenviada (12s)**")
                st.markdown("""
                > *Transcripción automática:*
                > "Víctor, habla Finanzas. El banco rechazó la prórroga. Si no liquidas inventario para el viernes, ejecutan la garantía. Necesitamos cash flow YA."
                """)

    # INPUT USUARIO
    if prompt := st.chat_input("Escribe tu respuesta..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Inyección de Prompt Dinámico
        instruccion = obtener_instruccion_sistema(st.session_state.turnos, st.session_state.nombre_alumno)
        prompt_final = f"{prompt} \n\n[SISTEMA - INSTRUCCIÓN OCULTA: {instruccion}]"
        
        bot_reply = None
        try:
            response = st.session_state.chat.send_message(prompt_final)
            bot_reply = response.text
        except Exception as e:
            st.error(f"Error de red: {e}")

        if bot_reply:
            # Detectar y Limpiar Etiquetas
            has_chart = False
            has_audio = False
            
            if "<GRAFICA_INVENTARIO>" in bot_reply:
                has_chart = True
                bot_reply = bot_reply.replace("<GRAFICA_INVENTARIO>", "").strip()
                
            if "<AUDIO_CONFIDENCIAL>" in bot_reply:
                has_audio = True
                bot_reply = bot_reply.replace("<AUDIO_CONFIDENCIAL>", "").strip()

            # Guardar en historial con banderas
            st.session_state.messages.append({
                "role": "model", 
                "content": bot_reply, 
                "has_chart": has_chart,
                "has_audio": has_audio
            })
            
            st.session_state.turnos += 1
            
            # Verificar Victoria
            if "Trato hecho" in bot_reply:
                st.balloons()
                st.success(f"🏆 ¡TRATO CERRADO! Felicidades, {st.session_state.nombre_alumno}. Has salvado el contrato.")
                st.session_state.active = False
            else:
                st.rerun()

else:
    st.markdown("### 🌲 Caso: Maderas Globales")
    st.info("👈 Ingresa tu nombre en el menú lateral para iniciar la llamada.")
