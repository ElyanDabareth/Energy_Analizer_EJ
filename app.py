import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="EnergyAnalyzer", page_icon="⚡", layout="wide")

st.title("⚡ EnergyAnalyzer: Consultoria Júnior")
st.markdown("Análise técnica de consumo e desperdício energético em comércios locais.")
st.divider()

# =========================
# CONSTANTES FÍSICAS
# =========================
TARIFA_MEDIA = 0.95  # R$/kWh

# =========================
# FUNÇÕES
# =========================
def calcular_consumo(potencia_w, horas_dia):
    """Calcula consumo mensal em kWh"""
    return (potencia_w * horas_dia * 30) / 1000


def calcular_custo(consumo_kwh):
    """Calcula custo energético"""
    return consumo_kwh * TARIFA_MEDIA


def calcular_economia(fatura):
    """Estimativa de economia (modelo simples para pitch)"""
    taxa_reducao = 0.18
    economia = fatura * taxa_reducao
    return economia, taxa_reducao


# =========================
# SIDEBAR (DADOS DO CLIENTE)
# =========================
st.sidebar.header("📋 Dados do Cliente")

cliente = st.sidebar.text_input("Nome do Estabelecimento", "Academia Fit")
tipo = st.sidebar.selectbox("Tipo", ["Academia", "Mercado", "Condomínio"])
fatura_atual = st.sidebar.number_input("Fatura Atual (R$)", min_value=0.0, value=1500.0)

# =========================
# INVENTÁRIO DE EQUIPAMENTOS
# =========================
st.subheader("🔍 Inventário de Equipamentos")

if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = []

with st.form("form_equipamentos"):
    col1, col2, col3 = st.columns(3)

    with col1:
        nome = st.text_input("Equipamento")
    with col2:
        potencia = st.number_input("Potência (W)", min_value=0.0)
    with col3:
        horas = st.slider("Horas/dia", 0, 24, 8)

    adicionar = st.form_submit_button("➕ Adicionar Equipamento")

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
# TABELA DE RESULTADOS
# =========================
if st.session_state.equipamentos:
    df = pd.DataFrame(st.session_state.equipamentos)

    st.subheader("📊 Consumo Detalhado")
    st.dataframe(df, use_container_width=True)

    consumo_total = df["Consumo (kWh)"].sum()
    custo_total = df["Custo (R$)"].sum()

    # =========================
    # MÉTRICAS
    # =========================
    st.subheader("📈 Indicadores Gerais")

    m1, m2, m3 = st.columns(3)

    m1.metric("Consumo Total", f"{consumo_total:.2f} kWh")
    m2.metric("Custo Estimado", f"R$ {custo_total:.2f}")

    economia, taxa = calcular_economia(fatura_atual)
    m3.metric("Economia Potencial", f"R$ {economia:.2f}", delta=f"-{int(taxa*100)}%")

    # =========================
    # GRÁFICOS
    # =========================
    st.subheader("📉 Análise Visual")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.bar_chart(df.set_index("Equipamento")["Consumo (kWh)"])

    with col_g2:
        dados_pitch = pd.DataFrame({
            "Cenário": ["Atual", "Com Consultoria"],
            "Custo (R$)": [fatura_atual, fatura_atual - economia]
        }).set_index("Cenário")

        st.bar_chart(dados_pitch)

    # =========================
    # IMPACTO ANUAL
    # =========================
    economia_anual = economia * 12

    st.success(
        f"✅ A {cliente} pode economizar aproximadamente "
        f"R$ {economia_anual:.2f} por ano."
    )

else:
    st.info("Adicione pelo menos um equipamento para iniciar a análise.")
