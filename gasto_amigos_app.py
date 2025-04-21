# BLOQUE 1: Importaciones necesarias
import streamlit as st
import pandas as pd
import datetime
import json
import gspread
from google.oauth2 import service_account

st.set_page_config(page_title="Gasto Justo – By NIKY'R", page_icon="💸", layout="centered")

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

# Mostrar la portada
st.image("https://raw.githubusercontent.com/Nikyr-dev/gasto-justo/main/encabezado_gasto_justo.png", use_container_width=True)

# Conectar con Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gspread"], scopes=SCOPE
)
cliente = gspread.authorize(credentials)
hoja = cliente.open_by_key("1OXuFe8wp0WxrsidTJX75eWQ0TH9oUtZB1nbhenbZMY0").sheet1

# Leer datos desde Google Sheets
datos = hoja.get_all_records()
gastos_df = pd.DataFrame(datos)

# Lista de participantes
participantes = ["Rama", "Nacho", "Marce"]

# BLOQUE 3: Menú lateral
opcion = st.sidebar.radio("📋 Navegación", ["Registrar Movimiento", "Historial de Gastos", "Análisis de Deudas"])

# BLOQUE 4: Registrar Movimiento
if opcion == "Registrar Movimiento":
    st.title("Registrar Nuevo Gasto")

    descripcion = st.text_input("¿Qué se compró?")
    monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
    pagador = st.selectbox("¿Quién pagó?", participantes)
    fecha = st.date_input("Fecha del gasto", datetime.date.today())
    quienes = st.multiselect("¿Quiénes participaron?", participantes, default=participantes)

    if st.button("Agregar gasto"):
        nuevo = [fecha.strftime("%Y-%m-%d"), descripcion, monto, pagador, json.dumps(quienes)]
        hoja.append_row(nuevo)
        st.success("✅ Gasto guardado correctamente.")
        st.experimental_rerun()

# BLOQUE 5: Historial de Gastos
elif opcion == "Historial de Gastos":
    st.title("Historial de Gastos")

    if not gastos_df.empty:
        for i, row in gastos_df.iterrows():
            participantes_gasto = ", ".join(json.loads(row["participantes"])) if isinstance(row["participantes"], str) else row["participantes"]
            st.markdown(f"- {row['fecha']} | **{row['descripcion']}** | ${row['monto']} – Pagó *{row['pagador']}* | Participaron: {participantes_gasto}")
    else:
        st.info("No hay gastos registrados aún.")

# BLOQUE 6: Análisis de Deudas
elif opcion == "Análisis de Deudas":
    st.title("Análisis de Deudas")

    if not gastos_df.empty:
        st.subheader("Saldos por persona")

        total_gastos = gastos_df["monto"].sum()
        promedio = total_gastos / len(participantes)

        saldo_individual = {}
        for nombre in participantes:
            pagado = gastos_df[gastos_df["pagador"] == nombre]["monto"].sum()
            saldo_individual[nombre] = pagado - promedio

        saldo_df = pd.DataFrame(list(saldo_individual.items()), columns=["Persona", "Saldo Final"])
        saldo_df["Estado"] = saldo_df["Saldo Final"].apply(lambda x: "Debe" if x < 0 else "A favor" if x > 0 else "Balanceado")
        st.dataframe(saldo_df.style.format({"Saldo Final": "${:,.2f}"}))

        st.divider()

        st.subheader("Detalle de Deudas")

        deudores = saldo_df[saldo_df["Saldo Final"] < 0].copy()
        acreedores = saldo_df[saldo_df["Saldo Final"] > 0].copy()

        for idx, deudor in deudores.iterrows():
            deuda = abs(deudor["Saldo Final"])
            for idx2, acreedor in acreedores.iterrows():
                if deuda == 0:
                    break
                pago = min(deuda, acreedor["Saldo Final"])
                if pago > 0:
                    st.markdown(f"🔸 **{deudor['Persona']} debe ${pago:,.2f} a {acreedor['Persona']}**")
                    saldo_df.loc[idx2, "Saldo Final"] -= pago
                    deuda -= pago
    else:
        st.info("No hay gastos cargados aún para analizar.")
