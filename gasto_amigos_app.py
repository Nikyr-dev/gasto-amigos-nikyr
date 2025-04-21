import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Gasto Justo - By NIKY'R", layout="centered")
st.title("Gasto Justo - By NIKY'R")

# Inicializar datos
if 'gastos' not in st.session_state:
    st.session_state.gastos = []

# Formulario para registrar gastos
st.header("Registrar nuevo gasto")
with st.form(key='nuevo_gasto'):
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto", min_value=0.0, format="%.2f")
    pagador = st.text_input("Pagador")
    participantes = st.text_input("Participantes (separados por coma)")
    fecha = st.date_input("Fecha", value=datetime.date.today())
    submit_button = st.form_submit_button(label='Agregar gasto')

if submit_button:
    participantes_lista = [p.strip() for p in participantes.split(',')]
    st.session_state.gastos.append({
        'descripcion': descripcion,
        'monto': monto,
        'pagador': pagador,
        'participantes': participantes_lista,
        'fecha': fecha
    })
    st.success("Gasto agregado exitosamente")

# Mostrar historial de gastos
st.header("Historial de gastos")
if st.session_state.gastos:
    gastos_df = pd.DataFrame(st.session_state.gastos)
    st.dataframe(gastos_df)

# Calcular deudas
st.header("Balance")

# Inicializar los totales
total_gastado = 0
balance_individual = {}
total_por_persona = {}

gastos = st.session_state.gastos

for gasto in gastos:
    monto = gasto['monto']
    participantes = gasto['participantes']
    pagador = gasto['pagador']
    total_gastado += monto

    # Inicializar si no existe el pagador
    if pagador not in total_por_persona:
        total_por_persona[pagador] = 0
    total_por_persona[pagador] += monto

    # Calcular cuánto debería pagar cada participante
    monto_por_participante = monto / len(participantes)

    for participante in participantes:
        if participante not in balance_individual:
            balance_individual[participante] = 0
        balance_individual[participante] -= monto_por_participante

    # El pagador recupera el total del gasto
    if pagador not in balance_individual:
        balance_individual[pagador] = 0
    balance_individual[pagador] += monto

st.subheader("Total gastado hasta ahora:")
st.write(f"${total_gastado:.2f}")

st.subheader("Saldos individuales:")
for persona, saldo in balance_individual.items():
    st.write(f"{persona}: ${saldo:.2f}")
