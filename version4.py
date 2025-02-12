import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora de Producción", layout="wide")

# CSS Premium para la aplicación
st.markdown("""
<style>
/* Fondo y tipografía */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #f4f6f9;
}
div.stApp {
    background: linear-gradient(to right, #ffffff, #e6e6e6);
}

/* Estilos para el título */
h1 {
    color: #333333;
    text-align: center;
}

/* Estilos para las tablas premium */
.custom-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}
.custom-table th, .custom-table td {
    padding: 12px 15px;
    border: 1px solid #dddddd;
    text-align: center;
}
.custom-table th {
    background-color: #4CAF50;
    color: white;
}
.custom-table tr:nth-child(even) {
    background-color: #f3f3f3;
}
.custom-table tr:hover {
    background-color: #f1f1f1;
}

/* Estilos para la barra de progreso de eficiencia */
.progress {
  background-color: #e0e0e0;
  border-radius: 13px;
  padding: 3px;
  margin: 0;
}
.progress-bar {
  background-color: #4CAF50;
  width: 0%;
  height: 20px;
  border-radius: 10px;
  text-align: center;
  color: white;
  line-height: 20px;
}
</style>
""", unsafe_allow_html=True)


def render_analysis_table(turno_minutos, tiempo_efectivo, tiempo_perdido, eficiencia):
    """
    Construye una tabla HTML con el análisis de tiempos, donde la fila de eficiencia
    se muestra como una barra de progreso.
    """
    eficiencia_percent = float(eficiencia)
    progress_bar_html = f'''
    <div class="progress">
      <div class="progress-bar" style="width: {eficiencia_percent}%; min-width: 50px;">
        {eficiencia_percent:.2f}%
      </div>
    </div>
    '''

    html = f'''
    <table class="custom-table">
      <tr>
        <th>Métrica</th>
        <th>Valor</th>
      </tr>
      <tr>
        <td>Tiempo Total del Turno</td>
        <td>{turno_minutos:.2f} min</td>
      </tr>
      <tr>
        <td>Tiempo Productivo</td>
        <td>{tiempo_efectivo:.2f} min</td>
      </tr>
      <tr>
        <td>Tiempo Perdido</td>
        <td>{tiempo_perdido:.2f} min</td>
      </tr>
      <tr>
        <td>Eficiencia</td>
        <td>{progress_bar_html}</td>
      </tr>
    </table>
    '''
    return html


def render_interruptions_table(interrupciones_dict, turno_minutos):
    """
    Construye una tabla HTML para el detalle de interrupciones con porcentaje del turno.
    """
    rows = ""
    for tipo, tiempo in interrupciones_dict.items():
        porcentaje = (tiempo / turno_minutos) * 100 if turno_minutos > 0 else 0
        rows += f"<tr><td>{tipo}</td><td>{tiempo:.2f} min</td><td>{porcentaje:.2f}%</td></tr>"

    html = f'''
    <table class="custom-table">
      <tr>
        <th>Tipo</th>
        <th>Tiempo (min)</th>
        <th>% del Turno</th>
      </tr>
      {rows}
    </table>
    '''
    return html


def calcular_produccion_216():
    st.title("🏭 Calculadora de Producción - Máquina 216")

    with st.expander("🔧 Configuración Operativa", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            turno_horas = st.number_input(
                "Duración del Turno (horas)",
                min_value=1.0, max_value=24.0, value=8.0, step=0.5
            )
            desayuno = st.checkbox("Incluir desayuno (15 min)")
            almuerzo = st.checkbox("Incluir almuerzo (60 min)")
        with col2:
            cambios_producto = st.number_input(
                "Cambios de producto", min_value=0, max_value=25, value=0, step=1
            )
            cambios_cuchillo = st.number_input(
                "Cambios de cuchillo", min_value=0, max_value=25, value=0, step=1
            )
            cambios_rollo = st.number_input(
                "Cambios de rollo", min_value=0, max_value=25, value=0, step=1
            )
            cambios_perforador = st.number_input(
                "Cambios de perforador", min_value=0, max_value=25, value=0, step=1
            )

    # Cálculo de tiempos
    turno_minutos = turno_horas * 60
    # Fijos: Calibración (10) + Comidas (15 y 60) + Otros (30)
    interrupciones_fijas = 10 + (15 if desayuno else 0) + (60 if almuerzo else 0) + 30
    # Variables: cambios de producto, cuchillo, rollo y perforador
    interrupciones_variables = (cambios_producto * 15) + (cambios_cuchillo * 30) + (cambios_rollo * 4) + (cambios_perforador * 10)
    tiempo_neto = turno_minutos - (interrupciones_fijas + interrupciones_variables)

    if tiempo_neto <= 0:
        st.error("⛔ Error: El tiempo de interrupciones excede la duración del turno")
        return

    # Ajuste por ciclo (27/32 efectivo, 5/32 detenciones automáticas)
    tiempo_efectivo = tiempo_neto * (27/32)
    tiempo_detenido_ciclos = tiempo_neto * (5/32)

    # Cálculo de producción
    unidades = 48 * tiempo_efectivo
    peso_kg = unidades * 45.3 / 1000

    # Cálculo de eficiencia
    eficiencia = (tiempo_efectivo / turno_minutos) * 100

    # Resultados principales
    st.success("📈 Resultados de Producción")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Unidades Estimadas", f"{unidades:,.0f}",
                  delta=f"Rango: {unidades * 0.96:,.0f} - {unidades * 1.04:,.0f}")
    with col2:
        st.metric("Peso Total Estimado", f"{peso_kg:,.1f} kg",
                  delta=f"Rango: {peso_kg * 0.96:,.1f} - {peso_kg * 1.04:,.1f} kg")

    # Tabla de Análisis de Tiempos
    st.subheader("⏳ Análisis de Tiempos")
    tiempo_perdido = turno_minutos - tiempo_efectivo
    analysis_html = render_analysis_table(turno_minutos, tiempo_efectivo, tiempo_perdido, eficiencia)
    with st.expander("Ver Análisis de Tiempos", expanded=True):
        st.markdown(analysis_html, unsafe_allow_html=True)

    # Detalle de interrupciones
    interrupciones_dict = {
        "Calibración": 10,
        "Comidas": (15 if desayuno else 0) + (60 if almuerzo else 0),
        "Otros": 30,
        "Cambios Producto": cambios_producto * 15,
        "Cambios Cuchillo": cambios_cuchillo * 30,
        "Cambios Rollo": cambios_rollo * 4,
        "Cambios Perforador": cambios_perforador * 10,
        "Paradas Automáticas": tiempo_detenido_ciclos
    }
    with st.expander("🔍 Detalle de Interrupciones", expanded=False):
        interruptions_html = render_interruptions_table(interrupciones_dict, turno_minutos)
        st.markdown(interruptions_html, unsafe_allow_html=True)


def calcular_produccion_235():
    st.title("🏭 Calculadora de Producción - Máquina 235")

    with st.expander("🔧 Configuración Operativa", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            turno_horas = st.number_input(
                "Duración del Turno (horas)",
                min_value=1.0, max_value=24.0, value=8.0, step=0.5, key="turno235"
            )
            desayuno = st.checkbox("Incluir desayuno (15 min)", key="desayuno235")
            almuerzo = st.checkbox("Incluir almuerzo (60 min)", key="almuerzo235")
        with col2:
            rollo_opcion = st.selectbox(
                "Tipo de rollo",
                options=["500 unidades", "700 unidades"],
                key="rollo_tipo"
            )
            cambios_rollo = st.number_input(
                "Cantidad de cambios de rollo", min_value=0, max_value=25, value=0, step=1, key="cambiosRollos235"
            )

    # Parámetros según opción de rollo
    if rollo_opcion == "500 unidades":
        unidades_por_rollo = 500
        peso_por_rollo = 1.38  # kg
    else:
        unidades_por_rollo = 700
        peso_por_rollo = 1.8   # kg

    # Cálculo de tiempos
    turno_minutos = turno_horas * 60
    # Tiempos fijos: Calibración (10) + Comidas (15 y 60) + Otros (30)
    interrupciones_fijas = 10 + (15 if desayuno else 0) + (60 if almuerzo else 0) + 30
    # Variable: Cambio de rollo (4 min cada)
    interrupciones_variables = cambios_rollo * 4
    tiempo_neto = turno_minutos - (interrupciones_fijas + interrupciones_variables)

    if tiempo_neto <= 0:
        st.error("⛔ Error: El tiempo de interrupciones excede la duración del turno")
        return

    # En la máquina 235 no hay ineficiencias de ciclo; tiempo efectivo = tiempo neto.
    tiempo_efectivo = tiempo_neto

    # Eficiencia
    eficiencia = (tiempo_efectivo / turno_minutos) * 100

    # Cálculo de producción:
    # La máquina produce a 248 GPM (unidades por minuto). Estas unidades se agrupan en rollos.
    total_unidades_producidas = 248 * tiempo_efectivo
    # Se calculan los rollos (resultado en forma continua, para estimación)
    rollos_producidos = total_unidades_producidas / unidades_por_rollo
    peso_total = rollos_producidos * peso_por_rollo

    # Resultados principales
    st.success("📈 Resultados de Producción")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rollos Estimados", f"{rollos_producidos:,.1f}",
                  delta=f"Rango: {rollos_producidos * 0.96:,.1f} - {rollos_producidos * 1.04:,.1f}")
    with col2:
        st.metric("Peso Total Estimado", f"{peso_total:,.2f} kg",
                  delta=f"Rango: {peso_total * 0.96:,.2f} - {peso_total * 1.04:,.2f} kg")

    # Tabla de Análisis de Tiempos
    st.subheader("⏳ Análisis de Tiempos")
    tiempo_perdido = turno_minutos - tiempo_efectivo
    analysis_html = render_analysis_table(turno_minutos, tiempo_efectivo, tiempo_perdido, eficiencia)
    with st.expander("Ver Análisis de Tiempos", expanded=True):
        st.markdown(analysis_html, unsafe_allow_html=True)

    # Detalle de interrupciones
    interrupciones_dict = {
        "Calibración": 10,
        "Comidas": (15 if desayuno else 0) + (60 if almuerzo else 0),
        "Cambio de Rollo": cambios_rollo * 4,
        "Otros": 30
    }
    with st.expander("🔍 Detalle de Interrupciones", expanded=False):
        interruptions_html = render_interruptions_table(interrupciones_dict, turno_minutos)
        st.markdown(interruptions_html, unsafe_allow_html=True)


# Selección de máquina (puedes usar la barra lateral o el cuerpo principal)
machine = st.sidebar.selectbox(
    "Seleccione la Máquina",
    options=["216", "235"],
    format_func=lambda x: "Máquina 216" if x == "216" else "Máquina 235"
)

if machine == "216":
    calcular_produccion_216()
else:
    calcular_produccion_235()
