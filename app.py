import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="EnergyAnalyzer", page_icon="⚡")

st.title("⚡ EnergyAnalyzer: Consultoria Júnior")
st.markdown("""
Esta ferramenta analisa o desperdício energético em comércios locais.
---
""")

# 1. ENTRADA DE DADOS (Barra Lateral)
st.sidebar.header("📋 Dados do Cliente")
cliente = st.sidebar.text_input("Nome do Estabelecimento", "Academia Fit")
tipo = st.sidebar.selectbox("Tipo", ["Academia", "Mercado", "Condomínio"])
fatura_atual = st.sidebar.number_input("Valor da Fatura (R$)", min_value=0.0, value=1500.0)

# 2. INVENTÁRIO DE CARGAS (Corpo Principal)
st.subheader("🔍 Inventário de Equipamentos")
col1, col2, col3 = st.columns(3)

with col1:
    equip = st.text_input("Equipamento", "Ar-Condicionado")
with col2:
    potencia = st.number_input("Potência (Watts)", value=2000)
with col3:
    horas = st.slider("Uso Diário (Horas)", 0, 24, 10)

# 3. CÁLCULOS TÉCNICOS
# Consumo Mensal = (Watts * Horas * 30 dias) / 1000
consumo_kwh = (potencia * horas * 30) / 1000
tarifa_media = 0.95  # Valor médio com impostos
custo_estimado = consumo_kwh * tarifa_media

# 4. RESULTADOS E MÉTRICAS
if st.button("🚀 Calcular Impacto"):
    st.divider()
    st.header(f"Resultado para {cliente}")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Consumo do Item", f"{consumo_kwh} kWh")
    m2.metric("Custo do Item", f"R$ {custo_estimado:.2f}")
    
    # Simulação de economia para o Pitch
    economia_potencial = fatura_atual * 0.18
    m3.metric("Economia Estimada", f"R$ {economia_potencial:.2f}", delta="-18%")

    # GRÁFICO PARA O PITCH
    st.subheader("Gráfico de Viabilidade")
    dados_grafico = pd.DataFrame({
        "Cenário": ["Gasto Atual", "Com nossa Consultoria"],
        "Valores (R$)": [fatura_atual, fatura_atual - economia_potencial]
    })
    st.bar_chart(data=dados_grafico, x="Cenário", y="Valores (R$)")
    
    st.success(f"✅ Com este projeto, a {cliente} economizaria R$ {economia_potencial * 12:.2f} por ano!")

    streamlit run app.py
