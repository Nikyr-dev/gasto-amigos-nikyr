# --- BLOQUE 1: Importaciones necesarias ---
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

st.set_page_config(page_title="Gasto Justo", page_icon="💸", layout="centered")

# --- BLOQUE 2: Fondo amarillo de la app ---
st.markdown(
    """
    <style>
    body {
        background-color: #FFF9C4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- BLOQUE 3: Conexión a Google Sheets ---
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
            "client_x509_cert_url": st.secrets["gspread"]["client_x509_cert_url"],
            "universe_domain": st.secrets["gspread"]["universe_domain"]
        },
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key("1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0")
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    connection_successful = True
except Exception as e:
    connection_successful = False
    error_msg = str(e)

# --- BLOQUE 4: Encabezado principal ---
st.image("https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/encabezado_gasto_justo.png", use_container_width=True)

# --- BLOQUE 5: Mostrar datos si hay conexión ---
if connection_successful:
    st.header("💸 Historial de Gastos")

    if not df.empty:
        # Mostrar historial
        for i, row in df.iterrows():
            participantes = row["participantes"].split(",") if isinstance(row["participantes"], str) else []
            participantes_texto = ", ".join(participantes)
            st.markdown(f"- {row['fecha']} | **{row['detalle']}** | ${row['monto']} – pagó *{row['pagador']}* | Participantes: {participantes_texto}")
    else:
        st.info("No hay gastos cargados todavía.")

    # --- BLOQUE 6: Análisis de Deudas ---
    st.header("📊 Análisis de Deudas")

    if not df.empty:
        personas = list(set(df["pagador"].unique().tolist() + sum(df["participantes"].apply(lambda x: x.split(",") if isinstance(x, str) else []), [])))
        personas = list(filter(None, personas))  # Eliminar vacíos

        saldos = {persona: 0 for persona in personas}

        for _, row in df.iterrows():
            monto = row["monto"]
            pagador = row["pagador"]
            participantes = row["participantes"].split(",") if isinstance(row["participantes"], str) else []

            if participantes:
                monto_por_persona = monto / len(participantes)
                for participante in participantes:
                    participante = participante.strip()
                    if participante != pagador:
                        saldos[participante] -= monto_por_persona
                        saldos[pagador] += monto_por_persona

        st.subheader("Resumen de saldos entre participantes:")
        for persona, saldo in saldos.items():
            if saldo > 0:
                st.success(f"✅ {persona} debe recibir ${saldo:.2f}")
            elif saldo < 0:
                st.warning(f"⚠️ {persona} debe pagar ${abs(saldo):.2f}")
            else:
                st.info(f"{persona} está en equilibrio 💸")
else:
    st.error("❌ Error de conexión con Google Sheets. Verificá tus credenciales y permisos.")
    st.text(f"Detalles: {error_msg}")
