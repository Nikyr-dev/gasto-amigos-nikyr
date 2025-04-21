# ----------------------------------------------
# gasto_amigos_app.py
# App Gasto Justo by NIKY’R
# ----------------------------------------------

import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# --- Configuración de página ---
st.set_page_config(page_title="Gasto Justo", page_icon="💸", layout="centered")

# --- Fondo amarillo ---
st.markdown(
    """
    <style>
    body {
        background-color: #FFF7D4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Portada ---
st.image("https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/portada_gastojusto.png", use_container_width=True)

# --- Conexión con Google Sheets ---
try:
    credentials = service_account.Credentials.from_service_account_info(
        {
            "type": st.secrets["gspread"]["type"],
            "project_id": st.secrets["gspread"]["project_id"],
            "private_key_id": st.secrets["gspread"]["private_key_id"],
            "private_key": st.secrets["gspread"]["private_key"],
            "client_email": st.secrets["gspread"]["client_email"],
            "client_id": st.secrets["gspread"]["client_id"],
            "auth_uri": st.secrets["gspread"]["auth_uri"],
            "token_uri": st.secrets["gspread"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gspread"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gspread"]["client_x509_cert_url"]
        }
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key('1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0')
    worksheet = sh.sheet1
    datos = worksheet.get_all_records()
    df = pd.DataFrame(datos)
except Exception as e:
    st.error(f"❌ Error de conexión con Google Sheets. Verificá tus credenciales y permisos.\n\nDetalles: {e}")
    st.stop()

# --- Menú de navegación ---
opcion = st.sidebar.radio("Ir a...", ["Registrar Gasto", "Historial de Gastos", "Balance de Cuentas"])

# --- Registrar Gasto ---
if opcion == "Registrar Gasto":
    st.title("Registrar Nuevo Gasto")

    descripcion = st.text_input("Descripción del gasto:")
    monto = st.number_input("Monto del gasto ($)", min_value=0.0, step=100.0)
    pagador = st.selectbox("¿Quién pagó?", ["Rama", "Nacho", "Marce"])
    participantes = st.multiselect("¿Quiénes participaron del gasto?", ["Rama", "Nacho", "Marce"], default=["Rama", "Nacho", "Marce"])

    if st.button("Guardar Gasto"):
        if descripcion and monto > 0 and participantes:
            nuevo_gasto = {
                "fecha": pd.Timestamp.now().strftime("%d-%b"),
                "detalle": descripcion,
                "monto": monto,
                "pagador": pagador,
                "participantes": ", ".join(participantes)
            }
            worksheet.append_row(list(nuevo_gasto.values()))
            st.success("✅ Gasto registrado correctamente.")
            st.experimental_rerun()
        else:
            st.warning("⚠️ Completá todos los campos antes de guardar.")

# --- Historial de Gastos ---
elif opcion == "Historial de Gastos":
    st.title("Historial de Gastos")
    if df.empty:
        st.info("Todavía no hay gastos registrados.")
    else:
        for _, row in df.iterrows():
            st.markdown(
                f"- {row['fecha']} | **{row['detalle']}** | ${row['monto']} – pagó *{row['pagador']}* | Participantes: {row['participantes']}"
            )

# --- Balance de Cuentas ---
elif opcion == "Balance de Cuentas":
    st.title("Balance de Cuentas")

    if not df.empty:
        participantes_unicos = ["Rama", "Nacho", "Marce"]
        saldos = {nombre: 0 for nombre in participantes_unicos}

        for _, row in df.iterrows():
            monto_total = row['monto']
            participantes_actuales = row['participantes'].split(", ")
            monto_por_persona = monto_total / len(participantes_actuales)

            for persona in participantes_actuales:
                saldos[persona] -= monto_por_persona

            saldos[row['pagador']] += monto_total

        st.subheader("Resumen:")
        for persona, saldo in saldos.items():
            if saldo > 0:
                st.success(f"💰 {persona} tiene saldo a favor de ${saldo:,.2f}")
            elif saldo < 0:
                st.error(f"💸 {persona} debe ${abs(saldo):,.2f}")
            else:
                st.info(f"🟰 {persona} está equilibrado.")
    else:
        st.info("Todavía no hay gastos registrados.")
