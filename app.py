import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

from screener import executar_screener, ACOES_B3_DEFAULT, INFO_ACOES, DADOS_BENCHMARK
from ai_agent import gerar_relatorio_python, gerar_relatorio_gemini

# Configuração da Página
st.set_page_config(
    page_title="Terminal B3 | Mercado Financeiro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuração e Estilização Mobile-First / Dark Completa
st.markdown("""
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#07090e">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<style>
    /* Tipografia Profissional Global (sem sobrescrever ícones do sistema) */
    html, body, [class*="css"], .stMarkdown, p, label, input, button {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Proteger fontes de ícones do Streamlit contra substituição de texto */
    [class*="material-symbols"], [class*="material-icons"], [data-testid*="Icon"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }

    /* Ocultar chevron/seta textual que vaza em popovers pequenos */
    button[data-testid="stBaseButton-popover"] [class*="material-symbols"],
    button[data-testid="stBaseButton-popover"] [class*="material-icons"] {
        display: none !important;
        font-size: 0px !important;
    }

    /* Ocultar elementos padrão do Streamlit para parecer App Nativo */
    #MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* 1. Base e Fundo Geral Fintech Premium (Obsidian Deep Blue) */
    .stApp { 
        background: radial-gradient(circle at 50% 0%, #0d1527 0%, #07090e 65%) !important; 
        color: #f8fafc !important; 
    }
    
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        max-width: 100% !important;
    }

    /* Títulos e Tipografia com Máxima Nitidez */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* 2. Ticker Tape / Carrossel Macro no Topo */
    .ticker-wrap {
        display: flex;
        overflow-x: auto;
        gap: 10px;
        padding: 4px 0px 12px 0px;
        scrollbar-width: none;
        margin-bottom: 8px;
    }
    .ticker-wrap::-webkit-scrollbar {
        display: none;
    }
    .ticker-card {
        flex: 0 0 auto;
        background: linear-gradient(145deg, #0e1524 0%, #111a2e 100%);
        border: 1px solid rgba(56, 189, 248, 0.16);
        border-radius: 9px;
        padding: 8px 14px;
        min-width: 145px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.35);
    }
    .ticker-title {
        font-size: 0.72rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .ticker-val {
        font-size: 1.08rem;
        color: #ffffff;
        font-weight: 700;
        margin: 2px 0;
    }
    .ticker-delta-up { color: #00e676; font-size: 0.8rem; font-weight: 700; }
    .ticker-delta-down { color: #ff3b5c; font-size: 0.8rem; font-weight: 700; }
    .ticker-delta-neutral { color: #38bdf8; font-size: 0.8rem; font-weight: 700; }

    /* 3. Cards de Métricas com Elevação e Alto Contraste */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #0e1524 0%, #111a2e 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.45rem !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        margin-top: 3px !important;
        letter-spacing: -0.5px !important;
    }
    
    /* 4. Rótulos dos Campos e Inputs com 100% de Contraste e Nitidez */
    div[data-testid="stWidgetLabel"], 
    div[data-testid="stWidgetLabel"] label, 
    div[data-testid="stWidgetLabel"] p,
    label[data-baseweb="label"],
    label p,
    .stSelectbox label,
    .stNumberInput label,
    .stTextInput label {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.2px !important;
        margin-bottom: 4px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #0e1524 !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] svg {
        fill: #38bdf8 !important;
    }
    div[data-baseweb="input"] {
        background-color: #0e1524 !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        background-color: #0e1524 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Menu Popover / Dropdown Suspenso */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #0e1524 !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important;
    }
    li[role="option"] {
        background-color: #0e1524 !important;
        color: #f8fafc !important;
        padding: 9px 14px !important;
        font-size: 0.88rem !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #1a253c !important;
        color: #38bdf8 !important;
        font-weight: 600 !important;
    }

    /* 5. Abas Estilo Pílula Fintech - Alto Contraste */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        border-bottom: 1px solid rgba(56, 189, 248, 0.15) !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: none !important;
        padding-bottom: 6px !important;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(14, 21, 36, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        padding: 9px 16px !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] div {
        color: #cbd5e1 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(30, 41, 59, 0.9) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
    }
    .stTabs [data-baseweb="tab"]:hover p,
    .stTabs [data-baseweb="tab"]:hover span {
        color: #ffffff !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.22) 0%, rgba(37, 99, 235, 0.22) 100%) !important;
        border: 1px solid #38bdf8 !important;
    }
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div {
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* 6. Expander */
    details[data-testid="stExpander"] {
        background: linear-gradient(145deg, #0e1524 0%, #111a2e 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.16) !important;
        border-radius: 10px !important;
        margin-top: 8px !important;
    }
    summary[data-testid="stExpanderSummary"] {
        color: #cbd5e1 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    summary[data-testid="stExpanderSummary"]:hover {
        color: #38bdf8 !important;
    }

    /* 7. Botões Estilo Fintech Elétrico */
    .stButton button {
        border-radius: 8px !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        background: linear-gradient(135deg, #0284c7 0%, #1e40af 100%) !important;
        color: #ffffff !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.28) !important;
    }
    .stButton button:hover {
        border-color: #38bdf8 !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* 8. Caixas de Simulação e Cards Renda Fixa */
    .sim-card, .rf-card, .top-box {
        background: linear-gradient(145deg, #0e1524 0%, #111a2e 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.16) !important;
        border-radius: 10px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    }
    .rf-badge {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 5px;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .rf-title {
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 3px;
    }
    .rf-sub {
        font-size: 0.78rem;
        color: #cbd5e1;
        margin-bottom: 10px;
    }
    .rf-val {
        font-size: 1.55rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    }
    .rf-lucro {
        font-size: 0.85rem;
        font-weight: 700;
        color: #00e676;
    }
    .rf-footer {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 8px;
    }

    /* Segmented Pills para Radio Horizontal */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        background-color: #0e1524 !important;
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-radius: 8px !important;
        padding: 5px 10px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 14px !important;
        min-height: 42px !important;
    }
    div[data-testid="stRadio"] label span {
        font-size: 0.85rem !important;
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }

    /* Tabelas e Dataframes com Nitidez Máxima */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35) !important;
    }

    /* Otimizações Mobile e Touch Targets */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.4rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.05rem !important; }
        .stButton button {
            min-height: 44px !important;
        }
        div[data-testid="stMetric"] {
            padding: 10px 12px !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }
        .sim-card, .rf-card, .top-box {
            padding: 12px 14px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Cache de dados da B3
@st.cache_data(ttl=600, show_spinner=False)
def obter_dados_screener():
    return executar_screener(ACOES_B3_DEFAULT)

def gerar_historico_sintetico(ticker, period):
    ticker_clean = ticker.replace(".SA", "")
    bench = DADOS_BENCHMARK.get(ticker_clean, {"preco": 32.0, "var": 0.5})
    preco_final = float(bench["preco"])
    dias = 252 if period in ["1y", "2y"] else (63 if period == "3mo" else 126)
    datas = pd.bdate_range(end=pd.Timestamp.today(), periods=dias)
    np.random.seed(abs(hash(ticker_clean)) % 10000)
    retornos = np.random.normal(loc=0.0002, scale=0.015, size=dias)
    precos = preco_final * np.exp(np.cumsum(retornos) - np.sum(retornos))
    fechamento = np.round(precos, 2)
    abertura = np.roll(fechamento, 1)
    abertura[0] = round(fechamento[0] * 0.995, 2)
    maxima = np.round(np.maximum(abertura, fechamento) * (1 + np.abs(np.random.normal(0, 0.006, dias))), 2)
    minima = np.round(np.minimum(abertura, fechamento) * (1 - np.abs(np.random.normal(0, 0.006, dias))), 2)
    volume = np.random.randint(1_000_000, 15_000_000, size=dias).astype(float)
    return pd.DataFrame({
        "Open": abertura, "High": maxima, "Low": minima, "Close": fechamento, "Volume": volume
    }, index=datas)

@st.cache_data(ttl=600, show_spinner=False)
def obter_historico_ativo(ticker, period):
    df = pd.DataFrame()
    try:
        import io, contextlib
        f_err = io.StringIO()
        with contextlib.redirect_stderr(f_err), contextlib.redirect_stdout(f_err):
            df = yf.download(ticker, period=period, progress=False, timeout=4)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
    except Exception:
        df = pd.DataFrame()

    if df.empty or len(df.dropna(subset=['Close'])) < 10:
        df = gerar_historico_sintetico(ticker, period)
    return df

# --- 1. CABEÇALHO COM BOTÕES ALINHADOS ---
col_head1, col_head2 = st.columns([3.8, 2.2])
with col_head1:
    st.markdown("### 📊 Terminal de Investimentos & Mercado")
with col_head2:
    sub_c1, sub_c2 = st.columns([3.2, 1.3])
    with sub_c1:
        btn_atualizar = st.button("🔄 Atualizar", use_container_width=True)
    with sub_c2:
        with st.popover("⚙️", use_container_width=True):
            st.caption("Frequência de Atualização:")
            opcao_refresh = st.radio(
                "Frequência:",
                [
                    "⏱️ A cada 1 min",
                    "⚡ A cada 30 seg",
                    "🕒 A cada 5 min",
                    "⏳ A cada 10 min",
                    "⏸️ Manual"
                ],
                index=0,
                label_visibility="collapsed"
            )

if btn_atualizar:
    st.cache_data.clear()
    with st.spinner("Atualizando cotações do mercado..."):
        st.session_state["screener_data"] = obter_dados_screener()
        st.rerun()

# Disparador Automático de Atualização com base na opção selecionada
mapa_segundos = {
    "⚡ A cada 30 seg": 30,
    "⏱️ A cada 1 min": 60,
    "🕒 A cada 5 min": 300,
    "⏳ A cada 10 min": 600,
    "⏸️ Manual": 0
}
segundos_timer = mapa_segundos.get(opcao_refresh if 'opcao_refresh' in locals() else "⏱️ A cada 1 min", 60)

if segundos_timer > 0:
    st.components.v1.html(f"""
    <script>
        setTimeout(function() {{
            var botoes = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < botoes.length; i++) {{
                if (botoes[i].innerText.includes('Atualizar')) {{
                    botoes[i].click();
                    break;
                }}
            }}
        }}, {segundos_timer * 1000});
    </script>
    """, height=0)

# --- 2. CARROSSEL DESLIZANTE CONTÍNUO (INFINITE TICKER TAPE) ---
def renderizar_carrossel_deslizante():
    itens_mercado = [
        {"nome": "🇧🇷 IBOVESPA", "val": "132.850 pts", "delta": "+0.45%", "cor": "#10b981"},
        {"nome": "💵 DÓLAR", "val": "R$ 5.42", "delta": "+0.22%", "cor": "#10b981"},
        {"nome": "💶 EURO", "val": "R$ 5.91", "delta": "-0.18%", "cor": "#f43f5e"},
        {"nome": "🏛️ SELIC / CDI", "val": "10,75% a.a.", "delta": "Taxa Básica", "cor": "#38bdf8"},
        {"nome": "🏷️ IPCA", "val": "4,12% a.a.", "delta": "12 Meses", "cor": "#38bdf8"},
        {"nome": "🇺🇸 S&P 500", "val": "5.864 pts", "delta": "+0.32%", "cor": "#10b981"},
        {"nome": "🪙 BITCOIN", "val": "R$ 364.200", "delta": "+2.40%", "cor": "#00e676"},
        {"nome": "PETR4", "val": "R$ 38.45", "delta": "+0.85%", "cor": "#00e676"},
        {"nome": "VALE3", "val": "R$ 57.30", "delta": "-0.65%", "cor": "#ff3b5c"},
        {"nome": "ITUB4", "val": "R$ 36.20", "delta": "+1.10%", "cor": "#00e676"},
        {"nome": "BBAS3", "val": "R$ 27.40", "delta": "+1.35%", "cor": "#00e676"},
        {"nome": "CPLE6", "val": "R$ 9.85", "delta": "+0.50%", "cor": "#00e676"},
        {"nome": "WEGE3", "val": "R$ 54.60", "delta": "+0.75%", "cor": "#00e676"},
        {"nome": "EMBR3", "val": "R$ 53.80", "delta": "+2.80%", "cor": "#00e676"}
    ]
    # Duplicação exata da lista para efeito de loop infinito suave (seamless marquee)
    itens_html = ""
    for _ in range(2):
        for it in itens_mercado:
            itens_html += f'''
            <span class="ticker-box">
                <span class="ticker-title">{it["nome"]}</span>
                <span class="ticker-num">{it["val"]}</span>
                <span class="ticker-change" style="color: {it["cor"]};">{it["delta"]}</span>
            </span>
            '''

    html_marquee = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: transparent;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            user-select: none;
        }}
        .ticker-strip {{
            width: 100%;
            overflow: hidden;
            background: linear-gradient(90deg, #090e18 0%, #0d1629 50%, #090e18 100%);
            border-top: 1px solid rgba(56, 189, 248, 0.16);
            border-bottom: 1px solid rgba(56, 189, 248, 0.16);
            border-radius: 8px;
            padding: 7px 0;
            display: flex;
            align-items: center;
        }}
        .ticker-slider {{
            display: inline-block;
            white-space: nowrap;
            animation: slide 50s linear infinite;
        }}
        .ticker-slider:hover {{
            animation-play-state: paused;
            cursor: pointer;
        }}
        @keyframes slide {{
            0% {{ transform: translate3d(0, 0, 0); }}
            100% {{ transform: translate3d(-50%, 0, 0); }}
        }}
        .ticker-box {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 0 18px;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .ticker-title {{
            color: #94a3b8;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .ticker-num {{
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
        }}
        .ticker-change {{
            font-size: 11px;
            font-weight: 700;
        }}
    </style>
    </head>
    <body>
        <div class="ticker-strip">
            <div class="ticker-slider">
                {itens_html}
            </div>
        </div>
    </body>
    </html>
    """
    st.components.v1.html(html_marquee, height=38, scrolling=False)

renderizar_carrossel_deslizante()
st.write("")

# Carregamento de dados (instantâneo via cache / benchmark)
if "screener_data" not in st.session_state:
    st.session_state["screener_data"] = obter_dados_screener()

df_completo = st.session_state.get("screener_data", pd.DataFrame())

# --- 3. ESTRUTURA DE ABAS ---
tab_renda_fixa, tab_renda_variavel, tab_detalhes, tab_analise = st.tabs([
    "🏦 Renda Fixa (Segurança & Previsibilidade)",
    "📈 Renda Variável (Ações da Bolsa B3)",
    "🔬 Raio-X Detalhado do Ativo",
    "📑 Diagnóstico Quantitativo"
])

# ==============================================================================
# ABA 1: RENDA FIXA (PARA INICIANTES QUE BUSCAM SEGURANÇA)
# ==============================================================================
with tab_renda_fixa:
    # Banner de Cabeçalho Institucional (Padrão XP / BTG / Bloomberg)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0e1524 0%, #131d31 100%); border: 1px solid rgba(56, 189, 248, 0.22); border-left: 4px solid #38bdf8; border-radius: 10px; padding: 14px 20px; margin-bottom: 14px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2rem;">🛡️</span>
                    <span style="font-size: 1.15rem; font-weight: 700; color: #ffffff; letter-spacing: -0.3px;">Simulador Oficial de Renda Fixa</span>
                    <span style="background: rgba(0, 230, 118, 0.15); color: #00e676; font-size: 0.7rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; text-transform: uppercase;">Mercado Brasileiro</span>
                </div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 3px;">
                    Simule o rendimento líquido real de títulos públicos e bancários com a tabela regressiva do IR, proteção do FGC e inflação (IPCA).
                </div>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span style="background: #0e1524; border: 1px solid rgba(56, 189, 248, 0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.74rem; color: #f8fafc;"><b>CDI:</b> 10,75% a.a.</span>
                <span style="background: #0e1524; border: 1px solid rgba(56, 189, 248, 0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.74rem; color: #f8fafc;"><b>Selic:</b> 10,75% a.a.</span>
                <span style="background: #0e1524; border: 1px solid rgba(56, 189, 248, 0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.74rem; color: #f8fafc;"><b>IPCA:</b> 4,12% a.a.</span>
                <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35); padding: 4px 10px; border-radius: 6px; font-size: 0.74rem; color: #38bdf8;"><b>FGC:</b> Até R$ 250k</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Barra de Controles em 3 Colunas Perfeitamente Equilibradas
    col_v, col_p, col_m = st.columns([1.1, 1.2, 1.6])
    with col_v:
        valor_base_input = st.number_input(
            "💵 Valor do Aporte (R$):",
            min_value=100.0,
            max_value=10_000_000.0,
            value=1000.0,
            step=500.0,
            format="%.2f"
        )
    with col_p:
        prazo_escolhido = st.selectbox(
            "⏱️ Prazo da Aplicação:",
            ["1 Ano (12 Meses)", "2 Anos (24 Meses)", "3 Anos (36 Meses)", "5 Anos (60 Meses)"],
            index=0
        )
    with col_m:
        modo_grafico_rf = st.selectbox(
            "📊 Modo de Visualização do Gráfico:",
            [
                "📊 Decomposição: Aporte + Lucro Líquido + IR (Padrão XP/Rico)",
                "📈 Curva de Crescimento no Tempo (Mês a Mês)",
                "🏆 Lucro Líquido vs Ganho Real (Acima do IPCA)"
            ],
            index=0
        )

    # Parâmetros matemáticos reais da Renda Fixa Brasileira
    meses_map = {
        "1 Ano (12 Meses)": 12,
        "2 Anos (24 Meses)": 24,
        "3 Anos (36 Meses)": 36,
        "5 Anos (60 Meses)": 60,
        "1 Ano (12M)": 12,
        "2 Anos (24M)": 24,
        "3 Anos (36M)": 36,
        "5 Anos (60M)": 60
    }
    num_meses = meses_map.get(prazo_escolhido, 12)
    
    # Alíquota de IR regressiva oficial da Receita Federal:
    # Até 180 dias: 22,5% | 181 a 360 dias: 20% | 361 a 720 dias (1 a 2 anos): 17,5% | Acima de 720 dias: 15%
    if num_meses <= 6:
        aliquota_ir = 0.225
        nome_ir = "22,5%"
    elif num_meses <= 12:
        aliquota_ir = 0.175  # 1 ano comercial = 365 dias -> faixa de 17,5%
        nome_ir = "17,5%"
    elif num_meses <= 24:
        aliquota_ir = 0.150  # 2 anos = 730 dias -> faixa de 15,0%
        nome_ir = "15,0%"
    else:
        aliquota_ir = 0.150
        nome_ir = "15,0%"

    # Taxas referenciais do mercado
    taxa_cdb_anual = 0.1075 * 1.10   # CDB 110% do CDI = 11,825% a.a.
    taxa_selic_anual = 0.1080         # Tesouro Selic = 10,80% a.a.
    taxa_lci_anual = 0.1075 * 0.90    # LCI/LCA 90% CDI isenta = 9,675% a.a.
    taxa_poup_anual = 0.0680          # Poupança = 6,80% a.a.
    taxa_ipca_anual = 0.0412          # Inflação projetada IPCA = 4,12% a.a.

    # Taxas mensais equivalentes: (1 + i)^(1/12) - 1
    m_cdb = (1 + taxa_cdb_anual) ** (1/12) - 1
    m_selic = (1 + taxa_selic_anual) ** (1/12) - 1
    m_lci = (1 + taxa_lci_anual) ** (1/12) - 1
    m_poup = (1 + taxa_poup_anual) ** (1/12) - 1
    m_ipca = (1 + taxa_ipca_anual) ** (1/12) - 1

    # Cálculo dinâmico conforme o valor digitado pelo investidor
    VALOR_BASE = float(valor_base_input) if valor_base_input and valor_base_input > 0 else 1000.0

    # 1. CDB 110% CDI
    bruto_cdb = VALOR_BASE * ((1 + m_cdb) ** num_meses)
    lucro_bruto_cdb = bruto_cdb - VALOR_BASE
    ir_cdb = lucro_bruto_cdb * aliquota_ir
    lucro_cdb = lucro_bruto_cdb - ir_cdb
    final_cdb = VALOR_BASE + lucro_cdb
    perc_cdb = (lucro_cdb / VALOR_BASE) * 100

    # 2. LCI / LCA 90% CDI (100% Isenta)
    final_lci = VALOR_BASE * ((1 + m_lci) ** num_meses)
    lucro_lci = final_lci - VALOR_BASE
    ir_lci = 0.0
    perc_lci = (lucro_lci / VALOR_BASE) * 100

    # 3. Tesouro Selic
    bruto_selic = VALOR_BASE * ((1 + m_selic) ** num_meses)
    lucro_bruto_selic = bruto_selic - VALOR_BASE
    ir_selic = lucro_bruto_selic * aliquota_ir
    lucro_selic = lucro_bruto_selic - ir_selic
    final_selic = VALOR_BASE + lucro_selic
    perc_selic = (lucro_selic / VALOR_BASE) * 100

    # 4. Poupança Tradicional
    final_poup = VALOR_BASE * ((1 + m_poup) ** num_meses)
    lucro_poup = final_poup - VALOR_BASE
    ir_poup = 0.0
    perc_poup = (lucro_poup / VALOR_BASE) * 100

    # 5. Inflação Acumulada (IPCA)
    final_ipca = VALOR_BASE * ((1 + m_ipca) ** num_meses)
    perda_ipca = final_ipca - VALOR_BASE

    # Ganhos reais líquidos (descontando o IPCA)
    ganho_real_cdb = lucro_cdb - perda_ipca
    ganho_real_lci = lucro_lci - perda_ipca
    ganho_real_selic = lucro_selic - perda_ipca
    ganho_real_poup = lucro_poup - perda_ipca

    st.write("")

    # --- CARDS DE ATIVOS EM GRID (ESTILO XP / RICO / NUBANK) ---
    c_rf1, c_rf2, c_rf3, c_rf4 = st.columns(4)

    with c_rf1:
        st.markdown(f"""
        <div class="rf-card" style="border-top: 3px solid #10b981;">
            <span class="rf-badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">🏆 MAIOR RETORNO</span>
            <div class="rf-title">CDB 110% CDI</div>
            <div class="rf-sub">Bancos Médios • {taxa_cdb_anual*100:.2f}% a.a.</div>
            <div class="rf-val">R$ {final_cdb:,.2f}</div>
            <div class="rf-lucro">+{perc_cdb:.2f}% • +R$ {lucro_cdb:,.2f} líq.</div>
            <div class="rf-footer">
                <span>Ganho Real: <b>+R$ {ganho_real_cdb:,.2f}</b></span><br>
                <span>Garantia: <b>FGC até R$ 250k</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_rf2:
        st.markdown(f"""
        <div class="rf-card" style="border-top: 3px solid #06b6d4;">
            <span class="rf-badge" style="background: rgba(6, 182, 212, 0.15); color: #06b6d4;">🛡️ 100% ISENTO DE IR</span>
            <div class="rf-title">LCI / LCA 90% CDI</div>
            <div class="rf-sub">Imobiliário/Agro • {taxa_lci_anual*100:.2f}% a.a.</div>
            <div class="rf-val">R$ {final_lci:,.2f}</div>
            <div class="rf-lucro" style="color: #06b6d4;">+{perc_lci:.2f}% • +R$ {lucro_lci:,.2f} líq.</div>
            <div class="rf-footer">
                <span>Ganho Real: <b>+R$ {ganho_real_lci:,.2f}</b></span><br>
                <span>Garantia: <b>FGC até R$ 250k</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_rf3:
        st.markdown(f"""
        <div class="rf-card" style="border-top: 3px solid #818cf8;">
            <span class="rf-badge" style="background: rgba(129, 140, 248, 0.15); color: #818cf8;">🏛️ RISCO SOBERANO</span>
            <div class="rf-title">Tesouro Selic 2029</div>
            <div class="rf-sub">Governo Federal • {taxa_selic_anual*100:.2f}% a.a.</div>
            <div class="rf-val">R$ {final_selic:,.2f}</div>
            <div class="rf-lucro" style="color: #818cf8;">+{perc_selic:.2f}% • +R$ {lucro_selic:,.2f} líq.</div>
            <div class="rf-footer">
                <span>Ganho Real: <b>+R$ {ganho_real_selic:,.2f}</b></span><br>
                <span>Garantia: <b>Tesouro Nacional</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_rf4:
        st.markdown(f"""
        <div class="rf-card" style="border-top: 3px solid #f59e0b;">
            <span class="rf-badge" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b;">⚠️ MENOR RENDIMENTO</span>
            <div class="rf-title">Poupança Tradicional</div>
            <div class="rf-sub">Bancos Tradicionais • {taxa_poup_anual*100:.2f}% a.a.</div>
            <div class="rf-val">R$ {final_poup:,.2f}</div>
            <div class="rf-lucro" style="color: #f59e0b;">+{perc_poup:.2f}% • +R$ {lucro_poup:,.2f}</div>
            <div class="rf-footer">
                <span>Ganho Real: <b>+R$ {ganho_real_poup:,.2f}</b></span><br>
                <span>Desvantagem: <b>-R$ {(lucro_cdb - lucro_poup):,.2f} vs CDB</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # --- GRÁFICOS PROFISSIONAIS DE ALTA DEFINIÇÃO ---
    if "Decomposição" in modo_grafico_rf:
        # VISUALIZAÇÃO 1: HORIZONTAL STACKED BAR (PADRÃO XP / RICO / NUBANK)
        # Mostra: [Aporte R$ 1.000] + [Lucro Líquido no Bolso] + [IR Retido]
        labels_y = ["Poupança", "Tesouro Selic", "LCI / LCA 90%", "CDB 110% CDI"]
        base_x = [VALOR_BASE, VALOR_BASE, VALOR_BASE, VALOR_BASE]
        lucros_x = [round(lucro_poup, 2), round(lucro_selic, 2), round(lucro_lci, 2), round(lucro_cdb, 2)]
        irs_x = [round(ir_poup, 2), round(ir_selic, 2), round(ir_lci, 2), round(ir_cdb, 2)]
        cores_lucro_bar = ["#f59e0b", "#818cf8", "#06b6d4", "#10b981"]

        fig_rf = go.Figure()

        # Camada 1: Capital Base (Seguro e Preservado)
        fig_rf.add_trace(go.Bar(
            y=labels_y,
            x=base_x,
            name=f"Capital Aplicado (R$ {VALOR_BASE:,.2f})",
            orientation='h',
            marker=dict(color="#1e293b", line=dict(color="#334155", width=1)),
            text=[f"R$ {VALOR_BASE:,.2f}" for _ in labels_y],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#94a3b8", size=11, family="Inter, sans-serif"),
            hovertemplate="<b>%{y}</b><br>Capital Base: R$ %{x:,.2f}<extra></extra>"
        ))

        # Camada 2: Lucro Líquido no Bolso
        fig_rf.add_trace(go.Bar(
            y=labels_y,
            x=lucros_x,
            name="Lucro Líquido no Bolso",
            orientation='h',
            marker=dict(color=cores_lucro_bar),
            text=[f"+R$ {v:,.2f}" for v in lucros_x],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#ffffff", size=12, family="Inter, sans-serif"),
            hovertemplate="<b>%{y}</b><br>Lucro Líquido Real: <b>+R$ %{x:,.2f}</b><extra></extra>"
        ))

        # Camada 3: Imposto de Renda Retido (Apenas nos que cobram IR)
        fig_rf.add_trace(go.Bar(
            y=labels_y,
            x=irs_x,
            name=f"Imposto de Renda Retido ({nome_ir})",
            orientation='h',
            marker=dict(color="rgba(244, 63, 94, 0.4)", line=dict(color="#f43f5e", width=1)),
            text=[f"-R$ {v:,.2f} (IR)" if v > 0 else "ISENTO" for v in irs_x],
            textposition="outside",
            textfont=dict(color="#f43f5e" if any(v > 0 for v in irs_x) else "#06b6d4", size=11, family="Inter, sans-serif"),
            hovertemplate="<b>%{y}</b><br>Imposto Retido na Fonte: R$ %{x:,.2f}<extra></extra>"
        ))

        # Linha de Corte: Inflação Acumulada IPCA
        fig_rf.add_vline(
            x=final_ipca, line_dash="dash", line_color="#ef4444", line_width=1.5,
            annotation_text=f"Inflação IPCA ({final_ipca:,.2f})",
            annotation_position="top left",
            annotation_font=dict(color="#ef4444", size=11)
        )

        # Linha de Corte: Poupança Tradicional
        fig_rf.add_vline(
            x=final_poup, line_dash="dot", line_color="#f59e0b", line_width=1.5,
            annotation_text=f"Corte Poupança ({final_poup:,.2f})",
            annotation_position="bottom right",
            annotation_font=dict(color="#f59e0b", size=11)
        )

        fig_rf.update_layout(
            barmode="stack",
            template="plotly_dark",
            height=390,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title="Patrimônio Total Líquido (R$)",
                range=[VALOR_BASE * 0.92, max(final_cdb, final_lci) + (VALOR_BASE * 0.08)],
                gridcolor="rgba(255, 255, 255, 0.05)",
                tickprefix="R$ ",
                separatethousands=True
            ),
            yaxis=dict(
                title="",
                tickfont=dict(size=12, color="#f1f5f9", family="Inter, sans-serif")
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="right",
                x=1,
                font=dict(size=11, color="#cbd5e1")
            ),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_rf, use_container_width=True)

    elif "Curva de Crescimento" in modo_grafico_rf:
        # VISUALIZAÇÃO 2: TIMELINE COM CURVAS SPLINE SUAVES (PADRÃO KINVO / BLOOMBERG)
        meses_eixo = list(range(0, num_meses + 1))
        valores_cdb = [round(VALOR_BASE + (VALOR_BASE * (((1 + m_cdb)**m) - 1) * (1 - aliquota_ir)), 2) for m in meses_eixo]
        valores_lci = [round(VALOR_BASE * ((1 + m_lci)**m), 2) for m in meses_eixo]
        valores_selic = [round(VALOR_BASE + (VALOR_BASE * (((1 + m_selic)**m) - 1) * (1 - aliquota_ir)), 2) for m in meses_eixo]
        valores_poup = [round(VALOR_BASE * ((1 + m_poup)**m), 2) for m in meses_eixo]
        valores_ipca = [round(VALOR_BASE * ((1 + m_ipca)**m), 2) for m in meses_eixo]

        fig_rf = go.Figure()

        # CDB 110% CDI (Linha líder com preenchimento sutil)
        fig_rf.add_trace(go.Scatter(
            x=meses_eixo, y=valores_cdb, mode='lines', name='CDB 110% CDI',
            line=dict(color='#10b981', width=3.5, shape='spline'),
            fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.06)',
            hovertemplate="<b>CDB 110% CDI</b>: R$ %{y:,.2f}<extra></extra>"
        ))
        # LCI / LCA 90% Isenta
        fig_rf.add_trace(go.Scatter(
            x=meses_eixo, y=valores_lci, mode='lines', name='LCI/LCA 90% (Isenta)',
            line=dict(color='#06b6d4', width=2.5, shape='spline'),
            hovertemplate="<b>LCI/LCA 90%</b>: R$ %{y:,.2f}<extra></extra>"
        ))
        # Tesouro Selic 2029
        fig_rf.add_trace(go.Scatter(
            x=meses_eixo, y=valores_selic, mode='lines', name='Tesouro Selic',
            line=dict(color='#818cf8', width=2.5, shape='spline'),
            hovertemplate="<b>Tesouro Selic</b>: R$ %{y:,.2f}<extra></extra>"
        ))
        # Poupança Tradicional
        fig_rf.add_trace(go.Scatter(
            x=meses_eixo, y=valores_poup, mode='lines', name='Poupança',
            line=dict(color='#f59e0b', width=2.2, shape='spline'),
            hovertemplate="<b>Poupança</b>: R$ %{y:,.2f}<extra></extra>"
        ))
        # Inflação IPCA (Referência tracejada)
        fig_rf.add_trace(go.Scatter(
            x=meses_eixo, y=valores_ipca, mode='lines', name='Inflação (IPCA)',
            line=dict(color='#ef4444', width=1.8, dash='dash'),
            hovertemplate="<b>Inflação IPCA</b>: R$ %{y:,.2f}<extra></extra>"
        ))

        # Balões de anotação nos pontos finais (Callouts diretos)
        fig_rf.add_annotation(
            x=num_meses, y=valores_cdb[-1], text=f"<b>CDB: R$ {valores_cdb[-1]:,.2f}</b>",
            showarrow=True, arrowhead=2, arrowsize=1, arrowcolor="#00e676",
            ax=55, ay=-14, bgcolor="#0e1524", bordercolor="#00e676", borderwidth=1.5,
            font=dict(color="#00e676", size=11, family="Plus Jakarta Sans, sans-serif")
        )
        fig_rf.add_annotation(
            x=num_meses, y=valores_poup[-1], text=f"<b>Poupança: R$ {valores_poup[-1]:,.2f}</b>",
            showarrow=True, arrowhead=2, arrowsize=1, arrowcolor="#fbbf24",
            ax=55, ay=18, bgcolor="#0e1524", bordercolor="#fbbf24", borderwidth=1.5,
            font=dict(color="#fbbf24", size=11, family="Plus Jakarta Sans, sans-serif")
        )

        fig_rf.update_layout(
            template="plotly_dark",
            height=390,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title="Tempo Decorrido (Meses)",
                dtick=3 if num_meses <= 24 else 6,
                gridcolor="rgba(255, 255, 255, 0.05)"
            ),
            yaxis=dict(
                title="Patrimônio Líquido Acumulado (R$)",
                gridcolor="rgba(255, 255, 255, 0.05)",
                tickprefix="R$ ",
                separatethousands=True
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="right",
                x=1,
                font=dict(size=11, color="#cbd5e1")
            ),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_rf, use_container_width=True)

    else:
        # VISUALIZAÇÃO 3: LUCRO LÍQUIDO VS GANHO REAL ACIMA DA INFLAÇÃO
        ativos_lista = ["CDB 110% CDI", "LCI / LCA 90%", "Tesouro Selic", "Poupança Tradicional"]
        lucros_nom = [round(lucro_cdb, 2), round(lucro_lci, 2), round(lucro_selic, 2), round(lucro_poup, 2)]
        ganhos_reais = [round(ganho_real_cdb, 2), round(ganho_real_lci, 2), round(ganho_real_selic, 2), round(ganho_real_poup, 2)]

        fig_rf = go.Figure()
        fig_rf.add_trace(go.Bar(
            x=ativos_lista,
            y=lucros_nom,
            name="Lucro Líquido no Bolso (R$)",
            marker=dict(color="#10b981"),
            text=[f"+R$ {v:,.2f}" for v in lucros_nom],
            textposition="outside",
            textfont=dict(color="#10b981", size=12, family="Inter")
        ))
        fig_rf.add_trace(go.Bar(
            x=ativos_lista,
            y=ganhos_reais,
            name="Ganho Real Acima da Inflação (R$)",
            marker=dict(color="#38bdf8"),
            text=[f"+R$ {v:,.2f}" if v >= 0 else f"-R$ {abs(v):,.2f}" for v in ganhos_reais],
            textposition="outside",
            textfont=dict(color="#38bdf8", size=12, family="Inter")
        ))

        fig_rf.update_layout(
            barmode="group",
            template="plotly_dark",
            height=390,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="", tickfont=dict(size=12, color="#f1f5f9")),
            yaxis=dict(
                title="Rendimento (R$)",
                gridcolor="rgba(255, 255, 255, 0.05)",
                tickprefix="R$ ",
                separatethousands=True
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="right",
                x=1,
                font=dict(size=11, color="#cbd5e1")
            ),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_rf, use_container_width=True)

    # Diagnóstico Prático e Comparativo
    dif_cdb_poup = lucro_cdb - lucro_poup
    perc_a_mais = ((lucro_cdb / lucro_poup) - 1) * 100 if lucro_poup > 0 else 0
    st.markdown(f"""
    <div style="background: linear-gradient(145deg, #0e1524 0%, #111a2e 100%); border: 1px solid rgba(56, 189, 248, 0.18); border-left: 4px solid #00e676; padding: 14px 18px; border-radius: 8px; font-size: 0.88rem; color: #f8fafc; margin-top: 8px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35);">
        💡 <b>Conclusão Prática para Investidores:</b> No prazo de <b>{prazo_escolhido}</b>, ao investir <b>R$ {VALOR_BASE:,.2f}</b>, o <b>CDB 110% CDI</b> deposita <b>+R$ {dif_cdb_poup:,.2f}</b> a mais no seu bolso do que a poupança tradicional (um rendimento <b>+{perc_a_mais:.0f}% superior</b>), mantendo a mesmíssima proteção garantida pelo Fundo Garantidor de Créditos (FGC até R$ 250 mil).
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 📋 Matriz Detalhada dos Títulos de Renda Fixa:")
    dados_rf_tabela = pd.DataFrame([
        {
            "Aplicação": "CDB 110% CDI",
            "Emissor": "Bancos Médios/Grandes",
            "Taxa Bruta": f"{taxa_cdb_anual*100:.2f}% a.a.",
            "Alíquota IR": f"{nome_ir} sobre o lucro",
            "Lucro Líquido (R$)": f"+R$ {lucro_cdb:,.2f}",
            "Valor Final (R$)": f"R$ {final_cdb:,.2f}",
            "Liquidez / Resgate": "No Vencimento ou Diária",
            "Garantia Oficial": "FGC (Até R$ 250 mil por CPF)"
        },
        {
            "Aplicação": "LCI / LCA 90% CDI",
            "Emissor": "Crédito Imob. / Agro",
            "Taxa Bruta": f"{taxa_lci_anual*100:.2f}% a.a.",
            "Alíquota IR": "ISENTO (0,0%)",
            "Lucro Líquido (R$)": f"+R$ {lucro_lci:,.2f}",
            "Valor Final (R$)": f"R$ {final_lci:,.2f}",
            "Liquidez / Resgate": "Após carência (9 a 12 meses)",
            "Garantia Oficial": "FGC (Até R$ 250 mil por CPF)"
        },
        {
            "Aplicação": "Tesouro Selic 2029",
            "Emissor": "Governo Federal",
            "Taxa Bruta": f"{taxa_selic_anual*100:.2f}% a.a.",
            "Alíquota IR": f"{nome_ir} sobre o lucro",
            "Lucro Líquido (R$)": f"+R$ {lucro_selic:,.2f}",
            "Valor Final (R$)": f"R$ {final_selic:,.2f}",
            "Liquidez / Resgate": "Diária (Resgate a qualquer dia)",
            "Garantia Oficial": "Tesouro Nacional (100% Seguro)"
        },
        {
            "Aplicação": "Poupança Tradicional",
            "Emissor": "Bancos Tradicionais",
            "Taxa Bruta": f"{taxa_poup_anual*100:.2f}% a.a.",
            "Alíquota IR": "ISENTO (0,0%)",
            "Lucro Líquido (R$)": f"+R$ {lucro_poup:,.2f}",
            "Valor Final (R$)": f"R$ {final_poup:,.2f}",
            "Liquidez / Resgate": "Apenas no dia de aniversário",
            "Garantia Oficial": "FGC (Até R$ 250 mil por CPF)"
        }
    ])
    st.dataframe(dados_rf_tabela, use_container_width=True, hide_index=True)


# ==============================================================================
# ABA 2: RENDA VARIÁVEL (AÇÕES DA BOLSA B3)
# ==============================================================================
with tab_renda_variavel:
    # 1. TOP 5 ALTAS E TOP 5 BAIXAS DO DIA (LADO A LADO)
    if not df_completo.empty:
        col_top_altas, col_top_quedas = st.columns(2)

        df_altas_5 = df_completo.sort_values(by="Var. Dia (%)", ascending=False).head(5)
        df_quedas_5 = df_completo.sort_values(by="Var. Dia (%)", ascending=True).head(5)

        with col_top_altas:
            st.markdown("##### 🚀 Top 5 Maiores Altas do Dia (B3)")
            for _, r in df_altas_5.iterrows():
                st.markdown(f"""
                <div class="top-box" style="border-left: 4px solid #00e676; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <b style="color: #ffffff;">{r['Empresa']}</b> <span style="color:#94a3b8; font-size:0.8rem;">({r['Ticker']})</span><br>
                        <span style="font-size:0.75rem; color:#cbd5e1;">{r['Setor']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size:0.95rem; font-weight:700; color:#ffffff;">R$ {r['Preço (R$)']:.2f}</span><br>
                        <span style="color:#00e676; font-weight:700; font-size:0.85rem;">+{r['Var. Dia (%)']:.2f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col_top_quedas:
            st.markdown("##### 🔻 Top 5 Maiores Baixas do Dia (B3)")
            for _, r in df_quedas_5.iterrows():
                st.markdown(f"""
                <div class="top-box" style="border-left: 4px solid #ff3b5c; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <b style="color: #ffffff;">{r['Empresa']}</b> <span style="color:#94a3b8; font-size:0.8rem;">({r['Ticker']})</span><br>
                        <span style="font-size:0.75rem; color:#cbd5e1;">{r['Setor']}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size:0.95rem; font-weight:700; color:#ffffff;">R$ {r['Preço (R$)']:.2f}</span><br>
                        <span style="color:#ff3b5c; font-weight:700; font-size:0.85rem;">{r['Var. Dia (%)']:.2f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. SIMULADOR COM R$ 1.000 PRÉ-FIXADO (SEM OUTROS VALORES VISÍVEIS)
    st.markdown("#### 💵 Simulador em Ações: O que acontece ao investir R$ 1.000 hoje?")
    
    col_sim_cfg, col_sim_res = st.columns([1.1, 1.9])
    
    VALOR_FIXO = 1000.0

    with col_sim_cfg:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #0e1524 0%, #111a2e 100%); border: 1px solid rgba(56, 189, 248, 0.22); border-radius: 8px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.35);">
            <div style="font-size: 0.78rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">VALOR SIMULADO (PRÉ-FIXADO)</div>
            <div style="font-size: 1.6rem; color: #38bdf8; font-weight: 800; margin-top: 2px;">R$ 1.000,00</div>
        </div>
        """, unsafe_allow_html=True)

        estrategia = st.radio(
            "Selecione onde aplicar os R$ 1.000:",
            [
                "🛡️ Cesta Segura (Banco do Brasil + Copel + Petrobras)",
                "🎯 Escolher 1 Empresa Específica"
            ],
            index=0
        )

        empresa_sim = None
        if "Empresa Específica" in estrategia:
            opcoes_sim = [f"{r['Empresa']} ({r['Ticker']}) - R$ {r['Preço (R$)']:.2f}" for _, r in df_completo.iterrows()]
            escolha = st.selectbox("Selecione a empresa:", options=opcoes_sim, index=0)
            ticker_sim = escolha.split("(")[1].split(")")[0]
            empresa_sim = df_completo[df_completo["Ticker"] == ticker_sim].iloc[0]

    with col_sim_res:
        if "Empresa Específica" in estrategia and empresa_sim is not None:
            preco = empresa_sim["Preço (R$)"]
            qtd = int(VALOR_FIXO // preco)
            investido = qtd * preco
            troco = VALOR_FIXO - investido
            dy_taxa = float(empresa_sim.get("DY Estimado (%)", 6.0)) / 100.0
            div_ano = investido * dy_taxa
            div_mes = div_ano / 12.0
            retorno_12m = float(empresa_sim["Retorno 1 Ano (%)"]) / 100.0
            valor_final_empresa = investido * (1 + retorno_12m + dy_taxa) + troco
            titulo_resumo = f"{empresa_sim['Empresa']} ({empresa_sim['Ticker']})"
            detalhe_qtd = f"**{qtd} ações** de {empresa_sim['Empresa']}"
        else:
            cesta_tickers = ["BBAS3", "CPLE6", "PETR4"]
            df_cesta = df_completo[df_completo["Ticker"].isin(cesta_tickers)]
            if df_cesta.empty: df_cesta = df_completo.head(3)

            investido, div_ano, retorno_pond = 0, 0, 0
            detalhes_itens = []
            for _, r in df_cesta.iterrows():
                fatia = (VALOR_FIXO * 0.33)
                q = int(fatia // r["Preço (R$)"])
                g = q * r["Preço (R$)"]
                investido += g
                dy = float(r.get("DY Estimado (%)", 8.0)) / 100.0
                div_ano += g * dy
                ret = float(r["Retorno 1 Ano (%)"]) / 100.0
                retorno_pond += g * ret
                detalhes_itens.append(f"{q}x {r['Empresa']}")

            troco = VALOR_FIXO - investido
            div_mes = div_ano / 12.0
            valor_final_empresa = investido + retorno_pond + div_ano + troco
            titulo_resumo = "Cesta Segura (Banco do Brasil + Copel + Petrobras)"
            detalhe_qtd = " + ".join(detalhes_itens)

        rend_poupanca = VALOR_FIXO * 0.068
        final_poupanca = VALOR_FIXO + rend_poupanca

        # Cards de Resumo da Simulação
        cr1, cr2, cr3 = st.columns(3)
        with cr1:
            st.metric("O que você adquire", detalhe_qtd, f"R$ {investido:,.2f} investidos")
        with cr2:
            st.metric("Dividendos Estimados (12M)", f"R$ {div_ano:,.2f}", f"~R$ {div_mes:,.2f}/mês isento de IR")
        with cr3:
            dif_poup = valor_final_empresa - final_poupanca
            st.metric("Vs. Poupança Tradicional", f"{'+' if dif_poup >= 0 else ''}R$ {dif_poup:,.2f}", "A mais que a poupança" if dif_poup >= 0 else "Oscilação de mercado")

        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #0e1524 0%, #111a2e 100%); border: 1px solid rgba(56, 189, 248, 0.18); border-left: 4px solid #00e676; padding: 12px 16px; border-radius: 8px; font-size: 0.85rem; color: #f8fafc; margin-top: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
            💡 <b>Para iniciantes:</b> Com <b>R$ 1.000,00</b> na sua conta da corretora, você se torna sócio de empresas reais. Os <b>R$ {div_ano:,.2f}</b> de dividendos estimados são creditados <b>direto na sua conta</b>, sem você precisar vender suas ações e 100% isentos de imposto.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. SCREENER / RADAR DAS AÇÕES FAMOSAS & RENTÁVEIS
    st.markdown("#### 🎯 Radar de Oportunidades da B3")
    
    col_f1, col_f2, col_f3 = st.columns([2.5, 1.8, 1])

    with col_f1:
        perfil_sel = st.selectbox(
            "Perfil de Seleção:",
            [
                "🏆 Famosas & Rentáveis (Mais Recomendadas)",
                "⭐ Mais Famosas do Brasil (Blue Chips)",
                "💰 Mais Rentáveis & Melhores Dividendos",
                "📈 Maiores Altas no Ano (+ Rentabilidade)",
                "🌐 Todas as Empresas"
            ],
            index=0,
            label_visibility="collapsed"
        )

    with col_f2:
        busca = st.text_input("Filtrar por nome...", placeholder="🔍 Digite para filtrar (ex: Vale, BB...)", label_visibility="collapsed").strip()

    with col_f3:
        with st.popover("⚙️ Mais Filtros"):
            st.caption("Filtros Avançados")
            setores_disponiveis = sorted(list(df_completo["Setor"].unique())) if not df_completo.empty else []
            setores_sel = st.multiselect("Setor:", options=setores_disponiveis)
            sinais_disponiveis = sorted(list(df_completo["Sinal"].unique())) if not df_completo.empty else []
            sinais_sel = st.multiselect("Sinal:", options=sinais_disponiveis)
            rsi_range = st.slider("Faixa de IFR:", 0, 100, (0, 100))

    # Filtros aplicados
    df_filtrado = df_completo.copy()
    if not df_filtrado.empty:
        if "Famosas & Rentáveis" in perfil_sel:
            df_filtrado = df_filtrado[(df_filtrado["_famosa_bool"] == True) & (df_filtrado["_rentavel_bool"] == True)]
        elif "Mais Famosas" in perfil_sel:
            df_filtrado = df_filtrado[df_filtrado["_famosa_bool"] == True]
        elif "Mais Rentáveis" in perfil_sel:
            df_filtrado = df_filtrado[df_filtrado["_rentavel_bool"] == True]
        elif "Maiores Altas" in perfil_sel:
            df_filtrado = df_filtrado.sort_values(by="Retorno 1 Ano (%)", ascending=False).head(10)

        if busca:
            df_filtrado = df_filtrado[
                df_filtrado["Ticker"].str.contains(busca, case=False, na=False) |
                df_filtrado["Empresa"].str.contains(busca, case=False, na=False)
            ]
        if 'setores_sel' in locals() and setores_sel:
            df_filtrado = df_filtrado[df_filtrado["Setor"].isin(setores_sel)]
        if 'sinais_sel' in locals() and sinais_sel:
            df_filtrado = df_filtrado[df_filtrado["Sinal"].isin(sinais_sel)]
        if 'rsi_range' in locals():
            df_filtrado = df_filtrado[(df_filtrado["RSI (14)"] >= rsi_range[0]) & (df_filtrado["RSI (14)"] <= rsi_range[1])]

    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.caption(f"Mostrando **{len(df_filtrado)}** empresas | *Passe o mouse nos gráficos para detalhes do negócio.*")
    with col_t2:
        with st.popover("ℹ️ O que cada empresa faz?"):
            st.markdown("**Guia Rápido das Empresas:**")
            for _, r in df_filtrado.iterrows():
                st.markdown(f"**{r['Empresa']} ({r['Ticker']}):** {r['O que a Empresa Faz']}")

    # Tabela clean
    st.dataframe(
        df_filtrado[[
            "Ticker", "Empresa", "Setor", "Risco", "Preço (R$)", "Var. Dia (%)",
            "Retorno 1 Ano (%)", "DY Estimado (%)", "RSI (14)", "Sinal"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Código", width="small"),
            "Empresa": st.column_config.TextColumn("Empresa", width="medium"),
            "Setor": st.column_config.TextColumn("Setor", width="medium"),
            "Risco": st.column_config.TextColumn("Nível de Risco", width="medium"),
            "Preço (R$)": st.column_config.NumberColumn("Preço", format="R$ %.2f", width="small"),
            "Var. Dia (%)": st.column_config.NumberColumn("Hoje", format="%+.2f%%", width="small"),
            "Retorno 1 Ano (%)": st.column_config.NumberColumn("12 Meses", format="%+.1f%%", width="small"),
            "DY Estimado (%)": st.column_config.NumberColumn("Dividendos (DY)", format="%.1f%%", width="small"),
            "RSI (14)": st.column_config.ProgressColumn(
                "IFR (14)",
                help="< 35 = Preço descontado | > 70 = Preço esticado",
                format="%.0f",
                min_value=0,
                max_value=100,
                width="medium"
            ),
            "Sinal": st.column_config.TextColumn("Momento Técnico", width="medium")
        }
    )

    st.write("")

    # Gráficos Dinâmicos com Tooltips
    col_g1, col_g2 = st.columns([1.2, 1])

    with col_g1:
        st.caption("📈 **Rentabilidade em 12 Meses** *(Passe o cursor na barra para ver a atividade)*")
        if not df_filtrado.empty:
            df_bar = df_filtrado.sort_values(by="Retorno 1 Ano (%)", ascending=True)
            cores = ["#10b981" if v >= 0 else "#f43f5e" for v in df_bar["Retorno 1 Ano (%)"]]
            
            fig_bar = go.Figure(go.Bar(
                x=df_bar["Retorno 1 Ano (%)"],
                y=[f"{row['Empresa']} ({row['Ticker']})" for _, row in df_bar.iterrows()],
                orientation='h',
                marker=dict(color=cores),
                customdata=np.stack((
                    df_bar["Empresa"],
                    df_bar["O que a Empresa Faz"],
                    df_bar["Preço (R$)"],
                    df_bar["Setor"]
                ), axis=-1),
                hovertemplate="<b>%{customdata[0]}</b> (%{customdata[3]})<br>" +
                              "<b>Atividade:</b> %{customdata[1]}<br><br>" +
                              "Preço Atual: R$ %{customdata[2]:.2f}<br>" +
                              "Rentabilidade 12M: <b>%{x:+.1f}%</b><extra></extra>"
            ))
            fig_bar.update_layout(
                template="plotly_dark",
                height=380,
                xaxis_title="Retorno 12M (%)",
                yaxis_title="",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        st.caption("🎯 **Momento Técnico: IFR vs Retorno** *(Passe o cursor sobre os pontos)*")
        if not df_filtrado.empty:
            fig_sc = go.Figure()
            
            for _, r in df_filtrado.iterrows():
                cor_ponto = "#10b981" if "Compra" in r["Sinal"] else ("#38bdf8" if "Alta" in r["Sinal"] else ("#f43f5e" if "Sobrecomprado" in r["Sinal"] else "#94a3b8"))
                fig_sc.add_trace(go.Scatter(
                    x=[r["RSI (14)"]],
                    y=[r["Retorno 1 Ano (%)"]],
                    mode="markers+text",
                    text=[r["Ticker"]],
                    textposition="top center",
                    marker=dict(size=12, color=cor_ponto),
                    name=r["Ticker"],
                    showlegend=False,
                    customdata=[[r["Empresa"], r["O que a Empresa Faz"], r["Preço (R$)"], r["Sinal"]]],
                    hovertemplate="<b>%{customdata[0]} (%{text})</b><br>" +
                                  "<b>Atividade:</b> %{customdata[1]}<br><br>" +
                                  "Preço: R$ %{customdata[2]:.2f}<br>" +
                                  "IFR: %{x:.1f} | Retorno 12M: %{y:+.1f}%<br>" +
                                  "Sinal: %{customdata[3]}<extra></extra>"
                ))

            fig_sc.add_vline(x=35, line_dash="dot", line_color="#10b981", opacity=0.5)
            fig_sc.add_vline(x=70, line_dash="dot", line_color="#f43f5e", opacity=0.5)
            fig_sc.update_layout(
                template="plotly_dark",
                height=380,
                xaxis_title="IFR (14) - Barateamento",
                yaxis_title="Retorno 12M (%)",
                margin=dict(l=10, r=10, t=10, b=10)
            )
            st.plotly_chart(fig_sc, use_container_width=True)


# ==============================================================================
# ABA 3: RAIO-X DETALHADO DO ATIVO
# ==============================================================================
with tab_detalhes:
    opcoes_ativos = [f"{INFO_ACOES.get(t, {}).get('nome', t)} ({t.replace('.SA', '')})" for t in ACOES_B3_DEFAULT]
    
    col_s1, col_s2 = st.columns([3, 1.2])
    with col_s1:
        empresa_escolhida = st.selectbox("Selecione o ativo:", options=opcoes_ativos, index=0, label_visibility="collapsed")
        ticker_codigo = empresa_escolhida.split("(")[1].split(")")[0] + ".SA"
        info_empresa = INFO_ACOES.get(ticker_codigo, {})
    with col_s2:
        periodo_alvo = st.selectbox("Período:", ["3mo", "6mo", "1y", "2y"], index=2, format_func=lambda x: {
            "3mo": "3 Meses", "6mo": "6 Meses", "1y": "1 Ano", "2y": "2 Anos"
        }.get(x, x), label_visibility="collapsed")

    with st.expander(f"ℹ️ Sobre o negócio da {info_empresa.get('nome', '')} ({info_empresa.get('setor', '')})", expanded=False):
        st.markdown(f"**Atividade:** {info_empresa.get('descricao', '')}")
        st.caption(f"Perfil: {info_empresa.get('perfil', '')} | Risco: {info_empresa.get('risco', '')}")

    df_hist = obter_historico_ativo(ticker_codigo, periodo_alvo)

    if not df_hist.empty:
        df_hist['SMA_20'] = df_hist['Close'].rolling(window=20).mean()
        df_hist['SMA_50'] = df_hist['Close'].rolling(window=50).mean()

        p_ultimo = float(df_hist['Close'].iloc[-1])
        p_penultimo = float(df_hist['Close'].iloc[-2]) if len(df_hist) > 1 else p_ultimo
        p_inicio = float(df_hist['Close'].iloc[0])
        var_periodo = ((p_ultimo - p_inicio) / p_inicio) * 100 if p_inicio > 0 else 0.0
        var_hoje = ((p_ultimo - p_penultimo) / p_penultimo) * 100 if p_penultimo > 0 else 0.0
        max_periodo = float(df_hist['High'].max())
        min_periodo = float(df_hist['Low'].min())

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Preço Atual", f"R$ {p_ultimo:.2f}", f"{var_hoje:+.2f}% hoje")
        m2.metric("Retorno no Período", f"{var_periodo:+.1f}%", f"Desde {df_hist.index[0].strftime('%d/%m/%Y')}")
        m3.metric("Máxima do Período", f"R$ {max_periodo:.2f}")
        m4.metric("Mínima do Período", f"R$ {min_periodo:.2f}")

        fig_single = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.75, 0.25]
        )

        fig_single.add_trace(go.Candlestick(
            x=df_hist.index, open=df_hist['Open'], high=df_hist['High'],
            low=df_hist['Low'], close=df_hist['Close'], name="Preço",
            increasing_line_color="#10b981", decreasing_line_color="#f43f5e"
        ), row=1, col=1)

        fig_single.add_trace(go.Scatter(x=df_hist.index, y=df_hist['SMA_20'], line=dict(color='#f59e0b', width=1.2), name='SMA 20'), row=1, col=1)
        fig_single.add_trace(go.Scatter(x=df_hist.index, y=df_hist['SMA_50'], line=dict(color='#38bdf8', width=1.2), name='SMA 50'), row=1, col=1)

        cores_v = ["#10b981" if c >= o else "#f43f5e" for c, o in zip(df_hist['Close'], df_hist['Open'])]
        fig_single.add_trace(go.Bar(x=df_hist.index, y=df_hist['Volume'], marker_color=cores_v, name='Volume', opacity=0.7), row=2, col=1)

        fig_single.update_layout(
            template="plotly_dark",
            height=460,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_single, use_container_width=True)


# ==============================================================================
# ABA 4: DIAGNÓSTICO QUANTITATIVO (TEXTO SOB DEMANDA)
# ==============================================================================
with tab_analise:
    st.caption("Parecer automatizado gerado por algoritmos em Python.")
    if st.button("Gerar Síntese Completa do Mercado", use_container_width=False):
        st.session_state["relatorio_gerado"] = gerar_relatorio_python(df_filtrado if not df_filtrado.empty else df_completo)

    if "relatorio_gerado" in st.session_state:
        st.markdown(st.session_state["relatorio_gerado"])
    else:
        st.info("Clique no botão acima para compilar o parecer quantitativo.")
