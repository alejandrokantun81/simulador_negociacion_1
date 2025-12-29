import streamlit as st
import google.generativeai as genai
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Negociación - Caso Maderas Globales",
    page_icon="🌲",
    layout="wide"
)

# --- 2. EL CEREBRO DE VÍCTOR KOVACS (LÓGICA DINÁMICA) ---
def obtener_instruccion_sistema(turno_actual):
    """
    Genera el prompt dinámico según el turno y las reglas del Dr. Kantún.
    """
    # Definición del Escenario
    contexto = """
    ROL: Eres el Sr. Víctor Kovacs, Director Comercial de 'Maderas Globales'.
    PERSONALIDAD: Arrogante, impaciente, pragmático y dominante. Frases cortas. Tono grave. Interrupciones frecuentes.
    SITUACIÓN: Llamada telefónica con un cliente.
    
    CONTEXTO OCULTO (TUS PROBLEMAS REALES):
    1. Crisis de Liquidez: Necesitas efectivo YA para deudas operativas.
    2. Saturación de Almacén: Tienes madera acumulada costando dinero.
    Públicamente exiges +25% por "costos logísticos", pero eso es una excusa.
    """
    
    # Dinámica de Turnos
    comportamiento_turno = ""
    if turno_actual <= 3:
        comportamiento_turno = "FASE HOSTIL (Turnos 1-3): Rechaza todo. Exige el 25% de aumento. Sé cortante."
    elif 4 <= turno_actual <= 7:
        comportamiento_turno = "FASE DE PISTAS (Turnos 4-7): Si el usuario muestra empatía o pregunta por tus problemas, da una pista vaga (ej: 'Tengo contenedores varados' o 'Necesito flujo de caja'). Si solo habla de precio, sigue hostil."
    elif 8 <= turno_actual <= 9:
        comportamiento_turno = "FASE DE PRESIÓN (Turnos 8-9): Di 'Tengo otra llamada entrando'. Exige cierre inmediato."
    else:
        comportamiento_turno = "FASE FINAL (Turno 10): Si no hay acuerdo exacto, di 'Se acabó el tiempo' y cuelga."

    # Condiciones de Victoria
    condiciones_victoria = """
    CONDICIONES PARA ACEPTAR EL TRATO (SI EL USUARIO DICE ESTO, ACEPTA INMEDIATAMENTE):
    
    OPCIÓN A (Financiera):
    - Usuario ofrece: Alza entre 12% y 15%.
    - CONDICIÓN: Pago Inmediato / De contado / Adelanto 50%.
    - TU RESPUESTA: "Mmm... El efectivo manda. Acepto el 15% por el pronto pago. Trato hecho."
    
    OPCIÓN B (Logística):
    - Usuario ofrece: Alza entre 12% y 15%.
    - CONDICIÓN: Doble volumen / Retiro inmediato de toda la mercancía.
    - TU RESPUESTA: "Bien. Me ayudas a limpiar el inventario. Acepto el 12% por el volumen. Trato hecho."
    
    SI NO CUMPLEN A o B: Rechaza con desprecio.
    """
    
    return f"{contexto}\n\nTURNO ACTUAL: {turno_actual}/10\nINSTRUCCIÓN DE COMPORTAMIENTO: {comportamiento_turno}\n{condiciones_victoria}"

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Caso: Maderas Globales")
    
    nombre_alumno = st.text_input("Nombre del Alumno")
    
    if st.button("Iniciar Llamada con el Sr. Kovacs 📞", type="primary"):
        try:
            # Opción A: Llave Institucional (Secrets)
            api_key = st.secrets["GOOGLE_API_KEY"]
            
            # Inicializar variables
            st.session_state.start_time = time.time()
            st.session_state.active = True
            st.session_state.messages = []
            st.session_state.turnos = 1 # Iniciamos en turno 1
            
            genai.configure(api_key=api_key)
            
            # --- CORRECCIÓN CRÍTICA: USAMOS EL ALIAS GENÉRICO ---
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # Iniciar chat (sin historial previo, el prompt se inyecta en cada mensaje)
            st.session_state.chat = model.start_chat(history=[])
            
            # Mensaje inicial de Kovacs
            initial_msg = "Maderas Globales, habla Kovacs. Tengo 2 minutos. ¿Para qué llama? Espero que sea para aceptar el aumento del 25%."
            st.session_state.messages.append({"role": "model", "content": initial_msg})
            st.session_state.chat.history.append({"role": "model", "parts": [initial_msg]})
            st.rerun()
            
        except Exception as e:
            st.error(f"Error al conectar: {e}")

# --- 4. ZONA PRINCIPAL ---
st.title("Simulador de Negociación: Maderas Globales 🌲")

if "active" not in st.session_state:
    st.session_state.active = False
if "turnos" not in st.session_state:
    st.session_state.turnos = 1

if st.session_state.active:
    # --- RELOJ Y CONTADOR DE TURNOS ---
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = 600 - elapsed_time
    
    if remaining_time <= 0 or st.session_state.turnos > 10:
        st.session_state.active = False
        st.error("📞 SE CORTÓ LA LLAMADA. (Tiempo o Turnos agotados)")
        st.stop()

    # Panel de control visual
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Turnos Utilizados", f"{st.session_state.turnos}/10")
    with col2:
        # Reloj JS
        components.html(f"""
        <div style="font-family:sans-serif; text-align:right; color:#555;">
            TIEMPO RESTANTE: <span id="cnt" style="color:#ff4b4b; font-weight:bold; font-size:1.5rem;">--:--</span>
        </div>
        <script>
            var t = {int(remaining_time)};
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

    # --- CHAT ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Responde al Sr. Kovacs..."):
        # 1. Mostrar mensaje del usuario
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 2. Preparar el Prompt con INYECCIÓN OCULTA
        instruccion_actual = obtener_instruccion_sistema(st.session_state.turnos)
        prompt_final = f"{prompt} \n\n[SISTEMA - INFORMACIÓN OCULTA PARA IA: {instruccion_actual}]"
        
        # 3. Obtener respuesta
        bot_reply = None
        try:
            response = st.session_state.chat.send_message(prompt_final)
            bot_reply = response.text
        except Exception as e:
            st.error(f"Error de red: {e}")

        # 4. Procesar respuesta y avanzar turno
        if bot_reply:
            with st.chat_message("model"):
                st.markdown(bot_reply)
            st.session_state.messages.append({"role": "model", "content": bot_reply})
            
            # Incrementar turno
            st.session_state.turnos += 1
            
            # Si el bot indica "Trato hecho", detener
            if "Trato hecho" in bot_reply or "trato hecho" in bot_reply:
                st.balloons()
                st.success("🏆 ¡NEGOCIACIÓN EXITOSA! Has cerrado el trato.")
                st.session_state.active = False
            else:
                st.rerun()

else:
    st.info("👈 Ingrese el nombre del alumno y presione Iniciar para llamar al cliente.")
    st.markdown("""
    **Misión:** Eres el Gerente de Compras. El proveedor (Sr. Kovacs) subió los precios un 25% injustificadamente.
    **Objetivo:** Negociar un aumento menor (12-15%) y asegurar el suministro.
    **Límite:** Tienes 10 minutos o 10 interacciones.
    """)
