# --- BLOQUE 1: Importaciones necesarias ---
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

# Configuración de la página
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

# --- BLOQUE 2: Cargar imagen de portada ---
st.image(
    "https://raw.githubusercontent.com/Nikyr-dev/gasto-amigos-nikyr/main/encabezado_gasto_justo.png",
    use_container_width=True
)

# --- BLOQUE 3: Conexión con Google Sheets ---
try:
    credentials = service_account.Credentials.from_service_account_info({
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
        "universe_domain": st.secrets["gspread"]["universe_domain"],
    })

    gc = gspread.authorize(credentials)
    sh = gc.open_by_key('1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0')
    worksheet = sh.sheet1
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)

except Exception as e:
    st.error("❌ Error de conexión con Google Sheets. Verificá tus credenciales y permisos.")
    st.stop()

# --- BLOQUE 4: Historial de Gastos ---
st.subheader("📜 Historial de Gastos")

if df.empty:
    st.info("Todavía no hay gastos registrados.")
else:
    for idx, row in df.iterrows():
        participantes = row["participantes"]
        participantes = participantes.replace("[", "").replace("]", "").replace("'", "")
        st.markdown(f"- {row['fecha']} | **{row['descripcion']}** | ${row['monto']:.2f} – pagó: *{row['pagador']}* | participantes: {participantes}")

# --- BLOQUE 5: Análisis de Deudas ---
st.subheader("💸 Análisis de Deudas")

try:
    # Participantes únicos
    participantes = set()

    for lista in df["participantes"]:
        if isinstance(lista, str):
            nombres = lista.replace("[", "").replace("]", "").replace("'", "").split(",")
            participantes.update([n.strip() for n in nombres])

    participantes = list(participantes)

    # Inicializar deuda
    deuda_individual = {nombre: 0 for nombre in participantes}

    # Calcular gastos individuales
    for idx, row in df.iterrows():
        monto = row["monto"]
        lista_participantes = row["participantes"]
        lista_participantes = lista_participantes.replace("[", "").replace("]", "").replace("'", "").split(",")
        lista_participantes = [n.strip() for n in lista_participantes]

        monto_por_persona = monto / len(lista_participantes)

        for p in lista_participantes:
            deuda_individual[p] += monto_por_persona

    # Cuánto pagó cada uno
    pagado = df.groupby("pagador")["monto"].sum().to_dict()

    # Mostrar balances
    for persona in participantes:
        gasto_teorico = deuda_individual.get(persona, 0)
        pago_real = pagado.get(persona, 0)
        balance = pago_real - gasto_teorico

        if balance > 0:
            st.success(f"✅ {persona} tiene saldo a favor de ${balance:.2f}")
        elif balance < 0:
            st.error(f"❌ {persona} debe pagar ${abs(balance):.2f}")
        else:
            st.info(f"⚖️ {persona} está justo, sin saldo ni deuda.")

except Exception as e:
    st.error("❌ Error procesando las deudas. Verificá que todos los registros estén completos.")

