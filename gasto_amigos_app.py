import streamlit as st
import datetime
import pywhatkit

amigos = {
    "Rama": "+5491124867312",  # reemplazá por tu número real
    "Nacho": "+5491169359577",
    "Marce": "+5493794652777"
}

st.title("💸 Gasto Justo - By NIKY’R")

descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto se gastó?", min_value=0.0, step=10.0)

st.subheader("¿Quiénes participaron?")
participantes = st.multiselect("Elegí quienes participaron", list(amigos.keys()))

st.subheader("¿Quién pagó?")
if participantes:
    pagador = st.selectbox("Elegí quién pagó", participantes)
else:
    pagador = None

if st.button("Dividir gasto y enviar WhatsApp"):
    if not descripcion or not monto or not participantes or not pagador:
        st.warning("Completá todos los campos")
    else:
        monto_por_persona = round(monto / len(participantes), 2)
        deudores = [p for p in participantes if p != pagador]

        hora = datetime.datetime.now().hour
        minuto = datetime.datetime.now().minute + 2

        st.success(f"{pagador} pagó ${monto} por '{descripcion}'")

        for d in deudores:
            numero = amigos[d]
            mensaje = (
                f"Hola {d}, {pagador} pagó ${monto} por: {descripcion}.\n"
                f"Te toca transferirle ${monto_por_persona}. - By NIKY’R"
            )
            try:
                pywhatkit.sendwhatmsg(numero, mensaje, hora, minuto)
                st.info(f"Mensaje programado para {d} a las {hora}:{minuto}")
                minuto += 1
            except Exception as e:
                st.error(f"Error enviando a {d}: {e}")
