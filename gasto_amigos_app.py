import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# Configurar página
st.set_page_config(page_title="Gasto Justo", page_icon="💸", layout="centered")

# Fondo
st.markdown(
    """
    <style>
    body {
        background-color: #FFF5E1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Portada
st.image("https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/portada_gasto_justo.png", use_container_width=True)

# Conectar a Google Sheets
try:
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gspread"],
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key("1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0")
    worksheet = sh.sheet1
    datos = worksheet.get_all_records()
    df = pd.DataFrame(datos)
except Exception as e:
    st.error(f"❌ Error de conexión con Google Sheets. Verificá tus credenciales y permisos.\n\nDetalles: {e}")
    st.stop()

# Participantes
participantes = ["Rama", "Nacho", "Marce"]

# Mostrar historial
st.header("Historial de Gastos")
if df.empty:
    st.info("No hay gastos registrados aún.")
else:
    for i, row in df.iterrows():
        participantes_texto = ', '.join(eval(row['participantes'])) if isinstance(row['participantes'], str) else ''
        st.markdown(f"- {row['fecha']} | **{row['detalle']}** | ${row['monto']} – pagó *{row['pagador']}* | Participantes: {participantes_texto}")

# Cálculo de balances
st.header("Saldos por persona")
if not df.empty:
    total_por_persona = {p: 0 for p in participantes}
    for i, row in df.iterrows():
        monto = row['monto']
        pagador = row['pagador']
        participantes_gasto = eval(row['participantes']) if isinstance(row['participantes'], str) else []
        
        if participantes_gasto:
            parte = monto / len(participantes_gasto)
            for p in participantes_gasto:
                total_por_persona[p] -= parte
            total_por_persona[pagador] += monto
    
    for persona, saldo in total_por_persona.items():
        if saldo > 0:
            st.success(f"✅ {persona} tiene saldo a favor de ${saldo:.2f}")
        elif saldo < 0:
            st.warning(f"⚠️ {persona} debe ${-saldo:.2f}")
        else:
            st.info(f"🔵 {persona} está en equilibrio.")

# Fin del archivo
