import streamlit as st
import datetime

# Título con íconos
st.markdown(
    """
    <h1 style='text-align: center; color: #ffc107; font-size: 42px;'>
        💸 Gasto Justo – <span style='color:#FF5252;'>By NIKY’R</span> 😢
    </h1>
    """,
    unsafe_allow_html=True
)

# Lista de participantes predefinidos
participantes_default = ["Rama", "Nacho", "Marce"]

# Estado inicial para guardar gastos
if "gastos" not in st.session_state:
    st.session_state.gastos = []

# Registro de nuevo gasto
st.subheader("Registrar nuevo gasto")

descripcion = st.text_input("¿Qué se compró?")
monto = st.number_input("¿Cuánto costó?", min_value=0.0, step=0.5)
pagador = st.selectbox("¿Quién pagó?", participantes_default)
fecha = st.date_input("Fecha del gasto", datetime.date.today())

if st.button("Agregar gasto"):
    nuevo_gasto = {
        "descripcion": descripcion,
        "monto": monto,
        "pagador": pagador,
        "fecha": fecha
    }
    st.session_state.gastos.append(nuevo_gasto)
    st.success("Gasto agregado correctamente")

# Mostrar historial de gastos
st.subheader("Historial de gastos")
if st.session_state.gastos:
    for gasto in st.session_state.gastos:
        st.markdown(f"- {gasto['fecha']} | **{gasto['descripcion']}** | ${gasto['monto']} – pagó *{gasto['pagador']}*")
else:
    st.info("Aún no se registraron gastos.")

# Calcular balances
st.subheader("Resumen de la semana")

if st.session_state.gastos:
    total = sum(g["monto"] for g in st.session_state.gastos)
    promedio = total / len(participantes_default)

    # Calcular cuánto pagó cada uno
    balances = {nombre: 0 for nombre in participantes_default}
    for gasto in st.session_state.gastos:
        balances[gasto["pagador"]] += gasto["monto"]

    st.markdown(f"**Total gastado:** ${total:.2f}")
    st.markdown(f"**Cada uno debería haber puesto:** ${promedio:.2f}")

    st.markdown("### Balance individual:")
    for nombre in participantes_default:
        diferencia = balances[nombre] - promedio
        if diferencia > 0:
            st.success(f"✅ {nombre} puso ${diferencia:.2f} de más")
        elif diferencia < 0:
            st.warning(f"⚠️ {nombre} debe ${abs(diferencia):.2f}")
        else:
            st.info(f"{nombre} está justo")

# Reiniciar semana (opcional)
if st.button("🧹 Reiniciar semana"):
    st.session_state.gastos = []
    st.success("Todos los gastos fueron reiniciados")
