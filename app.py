import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="EnergyAnalyzer", page_icon="⚡", layout="wide")

st.title("⚡ EnergyAnalyzer: Diagnóstico Energético Inteligente")
st.markdown("Transformando consumo de energia em decisões estratégicas.")
st.divider()

# =========================
# CONSTANTES
# =========================
TARIFA_MEDIA = 0.95  # R$/kWh

# =========================
# FUNÇÕES
# =========================
def calcular_consumo(potencia_w, horas_dia):
    return (potencia_w * horas_dia * 30) / 1000


def calcular_custo(consumo_kwh):
    return consumo_kwh * TARIFA_MEDIA


def classificar_consumo(p):
    if p > 0.4:
        return "🔴 Alto impacto"
    elif p > 0.2:
        return "🟡 Médio impacto"
    else:
        return "🟢 Baixo impacto"


# =========================
# SIDEBAR
# =========================
st.sidebar.header("📋 Dados do Cliente")

cliente = st.sidebar.text_input("Nome do Estabelecimento", "Academia Fit")
tipo = st.sidebar.selectbox("Tipo", ["Academia", "Mercado", "Condomínio"])
fatura_atual = st.sidebar.number_input("Fatura Atual (R$)", min_value=0.0, value=1500.0)

# =========================
# ESTADO
# =========================
if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = []

# =========================
# INVENTÁRIO
# =========================
st.subheader("🔍 Inventário de Equipamentos")

with st.form("form_equipamentos"):
    col1, col2, col3 = st.columns(3)

    with col1:
        nome = st.text_input("Equipamento")
    with col2:
        potencia = st.number_input("Potência (W)", min_value=0.0)
    with col3:
        horas = st.slider("Horas/dia", 0, 24, 8)

    adicionar = st.form_submit_button("➕ Adicionar")

    if adicionar and nome:
        consumo = calcular_consumo(potencia, horas)
        custo = calcular_custo(consumo)

        st.session_state.equipamentos.append({
            "Equipamento": nome,
            "Potência (W)": potencia,
            "Horas/dia": horas,
            "Consumo (kWh)": consumo,
            "Custo (R$)": custo
        })

# =========================
# ANÁLISE
# =========================
if st.session_state.equipamentos:
    df = pd.DataFrame(st.session_state.equipamentos)

    # Ordenação
    df = df.sort_values("Consumo (kWh)", ascending=False)

    # Pareto
    df["% Consumo"] = df["Consumo (kWh)"] / df["Consumo (kWh)"].sum()
    df["% Acumulado"] = df["% Consumo"].cumsum()

    # Classificação
    df["Impacto"] = df["% Consumo"].apply(classificar_consumo)

    # =========================
    # DIAGNÓSTICO
    # =========================
    st.subheader("📊 Diagnóstico Energético")

    consumo_total = df["Consumo (kWh)"].sum()
    custo_total = df["Custo (R$)"].sum()

    m1, m2 = st.columns(2)
    m1.metric("Consumo Total", f"{consumo_total:.2f} kWh")
    m2.metric("Custo Estimado", f"R$ {custo_total:.2f}")

    st.dataframe(df, use_container_width=True)

    # =========================
    # INTELIGÊNCIA
    # =========================
    st.subheader("🧠 Análise de Consumo (Prioridade)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏆 Ranking")
        st.bar_chart(df.set_index("Equipamento")["Consumo (kWh)"])

    with col2:
        st.markdown("### 📉 Pareto (%)")
        st.line_chart(df.set_index("Equipamento")["% Acumulado"])

    # =========================
    # SIMULAÇÃO
    # =========================
    st.subheader("🎯 Simulação de Intervenção")

    top = df.iloc[0]

    st.markdown(f"""
    **Equipamento mais relevante:** {top['Equipamento']}  
    Participação no consumo: {top['% Consumo']:.2%}
    """)

    reducao = st.slider("Redução no principal equipamento (%)", 0, 50, 20)

    economia_kwh = top["Consumo (kWh)"] * (reducao / 100)
    economia_reais = economia_kwh * TARIFA_MEDIA

    m1, m2 = st.columns(2)

    m1.metric("Economia Mensal", f"R$ {economia_reais:.2f}")
    m2.metric("Economia Anual", f"R$ {economia_reais * 12:.2f}")

    # =========================
    # COMPARAÇÃO FINAL
    # =========================
    st.subheader("📈 Impacto Financeiro")

    dados_pitch = pd.DataFrame({
        "Cenário": ["Atual", "Após Intervenção"],
        "Custo (R$)": [fatura_atual, fatura_atual - economia_reais]
    }).set_index("Cenário")

    st.bar_chart(dados_pitch)

    st.success(
        f"✅ Potencial de economia anual: R$ {economia_reais * 12:.2f}"
    )

else:
    st.info("Adicione equipamentos para iniciar a análise.")
