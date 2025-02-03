import streamlit as st


def calcular_produccion():
    st.title("Calculadora de Producción ( Máquina 216)")

    with st.expander("⚙️ Configuración de la Máquina", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            rango = st.radio("Rango de operación:",
                             ("Rango 1 (60-100 micras)", "Rango 2 (100-150 micras)"))

        with col2:
            velocidad = st.number_input("Velocidad programada (cpm)", 0.0, 100.0, 65.0)
            perforaciones = st.checkbox("Presencia de perforaciones")


    with st.expander("⏱ Parámetros del Turno", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            turno_horas = st.number_input("Duración del turno (horas)", 1.0, 24.0, 8.0)

        with col2:
            st.write("**Interrupciones programadas:**")
            cambios_producto = st.number_input("Cambios de producto", 0, 10, 0)
            cambios_cuchillo = st.number_input("Cambios de cuchillo", 0, 10, 0)
            cambios_rollo = st.number_input("Cambios de rollo", 0, 10, 0)

    # Validación de velocidad por rango
    rangos = {
        "Rango 1 (60-100 micras)": (65, 70),
        "Rango 2 (100-150 micras)": (55, 60)
    }

    min_vel, max_vel = rangos[rango]

    if not perforaciones and not (min_vel <= velocidad <= max_vel):
        st.error(f"⚠️ Velocidad fuera de rango! Para {rango} debe ser entre {min_vel}-{max_vel} cpm")
        return

    # Cálculo de tiempos
    turno_minutos = turno_horas * 60
    interrupciones_fijas = 15 + 60 + 10  # Desayuno + Almuerzo + Calibración
    interrupciones_variables = (cambios_producto * 15) + (cambios_cuchillo * 30) + (cambios_rollo * 4)
    tiempo_neto = turno_minutos - (interrupciones_fijas + interrupciones_variables)

    if tiempo_neto <= 0:
        st.error("⛔ Tiempo insuficiente! Las interrupciones superan la duración del turno")
        return

    # Ajuste por paradas técnicas
    tiempo_efectivo = tiempo_neto * (27 / 32)
    tiempo_detenido_ciclos = tiempo_neto * (5 / 32)  # Nuevo cálculo

    # Velocidad real
    velocidad_real = 47 if perforaciones else velocidad

    # Cálculo de producción
    unidades = velocidad_real * tiempo_efectivo
    peso_kg = unidades * 45.4 / 1000

    # Resultados
    st.success("📊 Resultados de Producción Estimados")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Unidades")
        st.metric(label="Producción Esperada",
                  value=f"{unidades:,.0f}",
                  delta=f"Rango: {unidades * 0.9:,.0f} - {unidades * 1.1:,.0f}")

    with col2:
        st.subheader("Peso")
        st.metric(label="Peso Total Estimado",
                  value=f"{peso_kg:,.1f} kg",
                  delta=f"Rango: {peso_kg * 0.9:,.1f} - {peso_kg * 1.1:,.1f} kg")

    # Detalles adicionales
    with st.expander("🔍 Detalles del Cálculo"):
        st.write(f"**Tiempo total del turno:** {turno_minutos} minutos")
        st.write(f"**Tiempo de interrupciones:** {interrupciones_fijas + interrupciones_variables} minutos")
        st.write(f"**Tiempo neto disponible:** {tiempo_neto:.1f} minutos")
        st.write(
            f"**Tiempo detenido por ciclos automáticos:** {tiempo_detenido_ciclos:.1f} minutos ({(tiempo_detenido_ciclos * 60):.0f} segundos)")
        st.write(f"**Eficiencia por paradas técnicas:** {27 / 32 * 100:.1f}%")
        st.write(f"**Tiempo efectivo de producción:** {tiempo_efectivo:.1f} minutos")
        st.write(f"**Velocidad efectiva:** {velocidad_real} cpm")


if __name__ == "__main__":
    calcular_produccion()