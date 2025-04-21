# BLOQUE 1: Importaciones necesarias
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# Configuración inicial de la página
st.set_page_config(page_title="Gasto Justo", page_icon="💸", layout="centered")

# Fondo amarillo Positano
st.markdown(
    """
    <style>
    body {
        background-color: #FFD93D;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Mostrar imagen de portada
st.image("https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/portada_gasto_justo.png", use_container_width=True)

# BLOQUE 2: Conexión a Google Sheets
credentials = service_account.Credentials.from_service_account_info(
    {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"],
    }
)
gc = gspread.authorize(credentials)
sh = gc.open_by_key('1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0')
worksheet = sh.sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Asegurar conversión correcta de participantes
if not df.empty:
    df["participantes"] = df["participantes"].apply(eval)

# BLOQUE 3: Mostrar Historial de Gastos
st.header("🧾 Historial de Gastos")
if not df.empty:
    for index, row in df.iterrows():
        participantes_str = ", ".join(row["participantes"])
        st.markdown(f"- {row['fecha']} | **{row['descripcion']}** | 💵 ${row['monto']:.2f} | 🧍‍♂️ {participantes_str}")
else:
    st.info("No hay gastos registrados todavía.")

# BLOQUE 4: Análisis de Deudas
st.header("💸 Balance y Deudas")
if not df.empty:
    # Calcular deudas
    saldo_individual = {nombre: 0 for nombre in ["Rama", "Nacho", "Marce"]}

    for i, row in df.iterrows():
        monto_total = row["monto"]
        participantes = row["participantes"]
        monto_individual = monto_total / len(participantes)
        pagador = row["pagador"]

        for persona in participantes:
            if persona != pagador:
                saldo_individual[persona] -= monto_individual
                saldo_individual[pagador] += monto_individual

    # Mostrar resultados
    for nombre, saldo in saldo_individual.items():
        if saldo > 0:
            st.success(f"✅ {nombre} tiene saldo a favor de ${saldo:.2f}")
        elif saldo < 0:
            st.warning(f"⚠️ {nombre} debe ${abs(saldo):.2f}")
        else:
            st.info(f"{nombre} está en equilibrio.")
else:
    st.info("No hay datos suficientes para calcular balances.")
