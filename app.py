import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

st.set_page_config(
    page_title="GuaduaTech Dashboard",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 GuaduaTech S.A.S.")
st.subheader("Auditoría Operacional, Balance de Masa, Energía y Costos")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("⚙️ Parámetros de Entrada")

meta_tableros = st.sidebar.number_input(
    "Meta de producción (tableros/semana)",
    min_value=100,
    value=1200
)

humedad_inicial = st.sidebar.slider(
    "Humedad inicial de la guadua (%)",
    min_value=50,
    max_value=90,
    value=83
)

humedad_final = st.sidebar.slider(
    "Humedad final antes del encolado (%)",
    min_value=8,
    max_value=10,
    value=9
)

temperatura_autoclave = st.sidebar.slider(
    "Temperatura del autoclave (°C)",
    min_value=110,
    max_value=130,
    value=120
)

eficiencia_caldera = st.sidebar.slider(
    "Eficiencia caldera (%)",
    min_value=50,
    max_value=100,
    value=85
)

costo_guadua = st.sidebar.number_input(
    "Costo Guadua (USD/ton)",
    min_value=1.0,
    value=80.0
)

costo_resina = st.sidebar.number_input(
    "Costo Resina (USD/kg)",
    min_value=0.1,
    value=2.5
)

tarifa_electricidad = st.sidebar.number_input(
    "Tarifa Electricidad (USD/kWh)",
    min_value=0.01,
    value=0.15
)

tarifa_vapor = st.sidebar.number_input(
    "Costo Vapor (USD/kg)",
    min_value=0.01,
    value=0.05
)

# --------------------------------------------------
# DATOS DEL BALANCE DE MASA
# --------------------------------------------------

etapas = [
    "Rajadora",
    "Cepilladora",
    "Autoclave",
    "Secadero",
    "Encoladora",
    "Prensa caliente",
    "Enfriamiento",
    "Desmolde",
    "Acabado final"
]

rendimientos = [
    0.85,
    0.40,
    0.95,
    0.90,
    0.98,
    0.95,
    1.00,
    1.00,
    0.8923
]

masa_inicial = 72000.0

entradas = []
salidas = []
mermas = []

masa = masa_inicial

for r in rendimientos:

    entrada = masa
    salida = masa * r
    merma = entrada - salida

    entradas.append(entrada)
    salidas.append(salida)
    mermas.append(merma)

    masa = salida

producto_final = salidas[-1]

df = pd.DataFrame({
    "Etapa": etapas,
    "Entrada (kg/sem)": entradas,
    "Salida (kg/sem)": salidas,
    "Merma (kg/sem)": mermas,
    "Rendimiento (%)": [r * 100 for r in rendimientos]
})

# --------------------------------------------------
# KPIs
# --------------------------------------------------

rendimiento_global = (producto_final / masa_inicial) * 100

merma_total = masa_inicial - producto_final

peso_tablero = producto_final / meta_tableros

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Balance de Masa",
    "⚡ Energía",
    "💰 Costos",
    "📊 Indicadores",
    "📥 Exportar"
])

# --------------------------------------------------
# TAB 1
# --------------------------------------------------

with tab1:

    st.header("Balance de Masa")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Materia Prima",
        f"{masa_inicial:,.0f} kg"
    )

    col2.metric(
        "Producto Final",
        f"{producto_final:,.0f} kg"
    )

    col3.metric(
        "Merma Total",
        f"{merma_total:,.0f} kg"
    )

    st.dataframe(df, use_container_width=True)

    fig1 = px.bar(
        df,
        x="Etapa",
        y=["Entrada (kg/sem)", "Salida (kg/sem)"],
        barmode="group",
        title="Entradas y Salidas por Etapa"
    )

    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        df,
        x="Etapa",
        y="Merma (kg/sem)",
        title="Mermas por Etapa"
    )

    st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# TAB 2
# --------------------------------------------------

with tab2:

    st.header("Balance Energético")

    kwh_rajadora = 15
    kwh_cepilladora = 20
    kwh_autoclave = 10
    kwh_secadero = 25
    kwh_prensa = 30

    toneladas = masa_inicial / 1000

    consumo_electrico = (
        (kwh_rajadora +
         kwh_cepilladora +
         kwh_autoclave +
         kwh_secadero +
         kwh_prensa)
        * toneladas
    )

    vapor_autoclave = 3000
    vapor_secadero = 5000
    vapor_prensa = 1500

    vapor_total = (
        vapor_autoclave +
        vapor_secadero +
        vapor_prensa
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Consumo Eléctrico",
        f"{consumo_electrico:,.0f} kWh/sem"
    )

    col2.metric(
        "Consumo de Vapor",
        f"{vapor_total:,.0f} kg/sem"
    )

    energia_df = pd.DataFrame({
        "Equipo": [
            "Rajadora",
            "Cepilladora",
            "Autoclave",
            "Secadero",
            "Prensa"
        ],
        "kWh/ton": [
            kwh_rajadora,
            kwh_cepilladora,
            kwh_autoclave,
            kwh_secadero,
            kwh_prensa
        ]
    })

    fig3 = px.pie(
        energia_df,
        names="Equipo",
        values="kWh/ton",
        title="Distribución Consumo Eléctrico"
    )

    st.plotly_chart(fig3, use_container_width=True)

# --------------------------------------------------
# TAB 3
# --------------------------------------------------

with tab3:

    st.header("Costos")

    costo_materia_prima = toneladas * costo_guadua

    resina_consumida = producto_final * 0.05

    costo_resina_total = (
        resina_consumida *
        costo_resina
    )

    costo_electricidad = (
        consumo_electrico *
        tarifa_electricidad
    )

    costo_vapor_total = (
        vapor_total *
        tarifa_vapor
    )

    costo_total = (
        costo_materia_prima +
        costo_resina_total +
        costo_electricidad +
        costo_vapor_total
    )

    costo_unitario = (
        costo_total /
        meta_tableros
    )

    costos_df = pd.DataFrame({
        "Concepto": [
            "Guadua",
            "Resina",
            "Electricidad",
            "Vapor"
        ],
        "USD": [
            costo_materia_prima,
            costo_resina_total,
            costo_electricidad,
            costo_vapor_total
        ]
    })

    st.dataframe(costos_df)

    st.metric(
        "Costo Unitario por Tablero",
        f"${costo_unitario:,.2f}"
    )

    fig4 = px.pie(
        costos_df,
        names="Concepto",
        values="USD",
        title="Distribución de Costos"
    )

    st.plotly_chart(fig4, use_container_width=True)

# --------------------------------------------------
# TAB 4
# --------------------------------------------------

with tab4:

    st.header("Indicadores")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Rendimiento Global",
        f"{rendimiento_global:.2f}%"
    )

    c2.metric(
        "Peso por Tablero",
        f"{peso_tablero:.2f} kg"
    )

    c3.metric(
        "Humedad Inicial",
        f"{humedad_inicial}%"
    )

    c4.metric(
        "Humedad Final",
        f"{humedad_final}%"
    )

    if masa_inicial < 72000:
        st.error(
            "⚠ Alerta de abastecimiento."
        )
    else:
        st.success(
            "✅ Materia prima suficiente."
        )

# --------------------------------------------------
# TAB 5
# --------------------------------------------------

with tab5:

    st.header("Exportar Resultados")

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Balance_Masa",
            index=False
        )

        costos_df.to_excel(
            writer,
            sheet_name="Costos",
            index=False
        )

    excel_data = output.getvalue()

    st.download_button(
        label="📥 Descargar Excel",
        data=excel_data,
        file_name="GuaduaTech_Resultados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.caption(
    "Dashboard académico para auditoría operacional de GuaduaTech S.A.S."
)
