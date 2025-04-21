# BLOQUE 1: Importaciones necesarias
import streamlit as st
import pandas as pd
import os
import datetime
import json

# Configuración de la página
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

# BLOQUE 2: Datos iniciales
participantes = ["Rama", "Nacho", "Marce"]

archivo = "gastos.csv"

# Cargar gastos desde el archivo
if os.path.exists(archivo):
    gastos_df = pd.read_csv(archivo)
else:
    gastos_df = pd.DataFrame(columns=["fecha", "descripcion", "monto", "pagador", "participantes"])

# BLOQUE 3: Menú lateral
opcion = st.sidebar.radio(
    "📋 Navegación",
    [
        "Registrar Movimiento",
        "Calendario",
        "Distribución Financiera",
        "Ahorros Auto",
        "Análisis de Deudas"
    ]
)

# BLOQUE 4: Registrar Movimiento
if opcion == "Registrar Movimiento":
    st.title("Registrar Nuevo Gasto")

    descripcion = st.text_input("¿Qué se compró?")
    monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
    pagador = st.selectbox("¿Quién pagó?", participantes)
    fecha = st.date_input("Fecha del gasto", datetime.date.today())
    quienes = st.multiselect("¿Quiénes participaron?", participantes, default=participantes)

    if st.button("Agregar gasto"):
        nuevo = pd.DataFrame([{
            "fecha": fecha.strftime("%Y-%m-%d"),
            "descripcion": descripcion,
            "monto": monto,
            "pagador": pagador,
            "participantes": json.dumps(quienes)
        }])
        gastos_df = pd.concat([gastos_df, nuevo], ignore_index=True)
        gastos_df.to_csv(archivo, index=False)
        st.success("✅ Gasto guardado correctamente.")
        st.experimental_rerun()  # Actualiza automáticamente la página

# BLOQUE 5: Calendario (provisorio)
elif opcion == "Calendario":
    st.title("🗓️ Calendario de Gastos")
    st.info("Modo calendario en desarrollo 🛠️")

# BLOQUE 6: Distribución Financiera estilo millonario
elif opcion == "Distribución Financiera":
    st.title("📊 Distribución Financiera Estilo Millonario")

    st.write("Ajustá los porcentajes de distribución:")

    ahorro = st.slider("Ahorro (%)", 0, 100, 10)
    inversion = st.slider("Inversión (%)", 0, 100, 10)
    fondo_auto = st.slider("Fondo para Auto (%)", 0, 100, 10)
    gastos_basicos = st.slider("Gastos Básicos (%)", 0, 100, 50)
    gastos_personales = st.slider("Gastos Personales (%)", 0, 100, 20)

    total = ahorro + inversion + fondo_auto + gastos_basicos + gastos_personales

    if total != 100:
        st.error(f"⚠️ La suma actual es {total}%. Debe ser 100%.")
    else:
        st.success("Distribución correcta 🎯")

# BLOQUE 7: Fondo Ahorro Auto
elif opcion == "Ahorros Auto":
    st.title("🚗 Fondo de Ahorro para el Auto")

    if not gastos_df.empty:
        try:
            gastos_df["participantes"] = gastos_df["participantes"].fillna("[]")
            df_auto = gastos_df[gastos_df["descripcion"].astype(str).str.contains("auto", case=False, na=False)]
            total_auto = df_auto["monto"].sum()
            st.metric(label="💸 Total Ahorrado para Auto", value=f"${total_auto:,.2f}")
            st.dataframe(df_auto)
        except Exception as e:
            st.error(f"Error procesando datos de ahorro auto: {e}")
    else:
        st.info("No hay datos cargados aún.")

# BLOQUE 8: Análisis de Deudas
elif opcion == "Análisis de Deudas":
    st.title("🔍 Análisis de Deudas")

    if not gastos_df.empty:
        st.subheader("Saldos por persona")

        total_gastos = gastos_df["monto"].sum()
        promedio = total_gastos / len(participantes)

        saldo_individual = {}
        for nombre in participantes:
            pagado = gastos_df[gastos_df["pagador"] == nombre]["monto"].sum()
            saldo_individual[nombre] = pagado - promedio

        # Mostramos tabla de saldos
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
