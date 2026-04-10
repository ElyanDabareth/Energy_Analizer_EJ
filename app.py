import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Lux | Consultoria Jr", 
    page_icon="⚡", 
    layout="wide"
)

# Custom CSS para melhorar a estética
st.markdown("""
    <style>
    .main {
        background-color: #467ce9;
    }
    .stMetric {
        background-color: #801e1e;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Lux: Diagnóstico Energético Inteligente")
st.markdown("**Solução Estratégica para Redução de Custos Fixos**")
st.divider()

# =========================
# CONSTANTES E ESTADO
# =========================
TARIFA_MEDIA = 0.95  # R$/kWh (Pode ser ajustado conforme a região)

if "equipamentos" not in st.session_state:
    st.session_state.equipamentos = []

# =========================
# SIDEBAR - CONFIGURAÇÕES
# =========================
st.sidebar.header("📋 Dados do Cliente")

cliente = st.sidebar.text_input("Nome do Estabelecimento", "Academia Fit")
tipo = st.sidebar.selectbox("Segmento", ["Academia", "Mercado", "Condomínio", "Outros"])
fatura_atual = st.sidebar.number_input("Valor da Fatura Atual (R$)", min_value=0.0, value=1500.0, step=50.0)

st.sidebar.divider()
st.sidebar.header("⚙️ Gestão de Dados")
if st.sidebar.button("🗑️ Resetar Diagnóstico"):
    st.session_state.equipamentos = []
    st.rerun()

# =========================
# FUNÇÕES DE CÁLCULO
# =========================
def calcular_consumo(potencia_w, horas_dia):
    return (potencia_w * horas_dia * 30) / 1000

def calcular_custo(consumo_kwh):
    return consumo_kwh * TARIFA_MEDIA

def classificar_impacto(p):
    if p > 0.4: return "🔴 Alto"
    elif p > 0.15: return "🟡 Médio"
    return "🟢 Baixo"

# =========================
# INVENTÁRIO (COM REPLICAÇÃO)
# =========================
st.subheader("🔍 Inventário de Equipamentos")

with st.form("form_equipamentos", clear_on_submit=True):
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        nome = st.text_input("Equipamento")
    with col2:
        potencia = st.number_input("Potência Unitária (W)", min_value=0.0, step=10.0)
    with col3:
        # CAMPO NOVO: Quantidade para replicar itens iguais
        quantidade = st.number_input("Qtd", min_value=1, value=1)
    with col4:
        horas = st.slider("Horas/dia", 0, 24, 8)

    adicionar = st.form_submit_button("➕ Adicionar ao Inventário")

    if adicionar and nome and potencia > 0:
        # O segredo está aqui: multiplicamos pela quantidade
        consumo_total_item = calcular_consumo(potencia, horas) * quantidade
        custo_total_item = calcular_custo(consumo_total_item)

        # Guardamos no nome algo como "Esteira (x10)" para ficar claro na tabela
        nome_exibicao = f"{nome} (x{quantidade})" if quantidade > 1 else nome

        st.session_state.equipamentos.append({
            "Equipamento": nome_exibicao,
            "Qtd": quantidade,
            "Potência Total (W)": potencia * quantidade,
            "Horas/dia": horas,
            "Consumo (kWh)": round(consumo_total_item, 2),
            "Custo (R$)": round(custo_total_item, 2)
        })
        st.rerun() # Atualiza a tela para mostrar o novo item imediatamente
# =========================
# PROCESSAMENTO E DASHBOARD
# =========================
if st.session_state.equipamentos:
    df = pd.DataFrame(st.session_state.equipamentos)

    # Cálculos de Pareto e Impacto
    total_kwh = df["Consumo (kWh)"].sum()
    df["% Consumo"] = df["Consumo (kWh)"] / total_kwh
    df = df.sort_values("% Consumo", ascending=False)
    df["Impacto"] = df["% Consumo"].apply(classificar_impacto)

    # --- MÉTRICAS PRINCIPAIS ---
    st.subheader("📊 Diagnóstico de Consumo")
    m1, m2, m3 = st.columns(3)
    
    custo_total_estimado = df["Custo (R$)"].sum()
    eficiencia_base = (custo_total_estimado / fatura_atual) if fatura_atual > 0 else 0

    m1.metric("Consumo Total", f"{total_kwh:.2f} kWh")
    m2.metric("Custo Identificado", f"R$ {custo_total_estimado:.2f}")
    m3.metric("Rastreabilidade", f"{eficiencia_base:.1%}", help="Quanto do valor da fatura foi identificado no inventário")
   # Adicione isso logo após os cálculos de custo total
    diferenca = fatura_atual - custo_total_estimado

    if diferenca > (fatura_atual * 0.3): # Se a diferença for maior que 30%
      st.warning(f"⚠️ Atenção: R$ {diferenca:.2f} do seu consumo não foram identificados. Isso pode indicar fugas de energia, fiação antiga ou erros de medição.")
    # Exibição da Tabela com Destaque
    st.dataframe(
        df.style.highlight_max(axis=0, subset=["Consumo (kWh)"], color="#ff4b4b33"),
        use_container_width=True
    )

    # --- VISUALIZAÇÃO ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏆 Maiores Consumidores")
        st.bar_chart(df.set_index("Equipamento")["Consumo (kWh)"])
    
    with c2:
        st.markdown("### 📈 Distribuição de Custos")
        # Gráfico simples de pizza/barras para impacto
        st.area_chart(df.set_index("Equipamento")["% Consumo"])

    # =========================
    # SIMULAÇÃO E VIABILIDADE
    # =========================
    st.divider()
    st.subheader("🎯 Proposta de Intervenção")
    
    item_critico = df.iloc[0]
    st.info(f"O item **{item_critico['Equipamento']}** representa {item_critico['% Consumo']:.1%} do seu consumo identificado. Focar aqui trará o maior retorno.")

    col_sim1, col_sim2 = st.columns([2, 1])
    
    with col_sim1:
        reducao_pct = st.slider("Meta de redução no item crítico (%)", 0, 100, 25)
        investimento_ej = st.number_input("Valor do Projeto (Investimento Único R$)", value=800.0)

    with col_sim2:
        economia_mensal = item_critico["Custo (R$)"] * (reducao_pct / 100)
        economia_anual = economia_mensal * 12
        
        st.metric("Economia Estimada", f"R$ {economia_mensal:.2f}/mês")
        
        if economia_mensal > 0:
            payback = investimento_ej / economia_mensal
            st.warning(f"**Payback:** {payback:.1f} meses")

    # Gráfico Final de Impacto no Bolso
    st.markdown("### 📈 Projeção Financeira Anual")
    dados_anual = pd.DataFrame({
        "Cenário": ["Sem Consultoria", "Com Consultoria"],
        "Custo Anual (R$)": [fatura_atual * 12, (fatura_atual * 12) - economia_anual]
    }).set_index("Cenário")
    
    st.bar_chart(dados_anual)
    
    st.success(f"💰 Ao final de um ano, o cliente terá **R$ {economia_anual:.2f}** extras em caixa.")

else:
    st.info("👋 Bem-vindo! Comece adicionando os equipamentos do cliente acima para gerar o diagnóstico.")
