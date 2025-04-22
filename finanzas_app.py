
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="FINANZAS", page_icon="💰", layout="centered")

st.markdown(
    "<h1 style='text-align: center; color: #4CAF50; font-size: 50px;'>💰 FINANZAS</h1>",
    unsafe_allow_html=True
)

archivo_datos = "movimientos_financieros.csv"

if Path(archivo_datos).exists():
    df = pd.read_csv(archivo_datos)
else:
    df = pd.DataFrame(columns=["fecha", "tipo", "categoría", "detalle", "monto"])

st.subheader("Registrar nuevo movimiento")

col1, col2 = st.columns(2)
with col1:
    tipo = st.selectbox("Tipo", ["Ingreso", "Egreso"])
    fecha = st.date_input("Fecha", datetime.date.today())
with col2:
    categoria = st.selectbox("Categoría", ["Sueldo", "Servicios", "Comida", "Transporte", "Salidas", "Otros"])
    monto = st.number_input("Monto", min_value=0.0, step=100.0)

detalle = st.text_input("Detalle (opcional)")

if st.button("Agregar"):
    nuevo = pd.DataFrame([{
        "fecha": fecha,
        "tipo": tipo,
        "categoría": categoria,
        "detalle": detalle,
        "monto": monto
    }])
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(archivo_datos, index=False)
    st.success("Movimiento registrado.")

st.subheader("Historial de movimientos")
if df.empty:
    st.info("Aún no se registraron movimientos.")
else:
    st.dataframe(df.sort_values("fecha", ascending=False), use_container_width=True)

ingresos = df[df["tipo"] == "Ingreso"]["monto"].sum()
egresos = df[df["tipo"] == "Egreso"]["monto"].sum()
balance = ingresos - egresos

st.subheader("Resumen general")
st.markdown(f"**Total ingresado:** ${ingresos:,.2f}")
st.markdown(f"**Total gastado:** ${egresos:,.2f}")
st.markdown(f"**Balance disponible:** ${balance:,.2f}")
