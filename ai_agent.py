import os
import pandas as pd

def gerar_relatorio_python(df_screener: pd.DataFrame) -> str:
    """Gera um relatório técnico e quantitativo detalhado em Python, sem necessidade de API externa."""
    if df_screener is None or df_screener.empty:
        return "⚠️ Nenhum dado disponível para análise. Execute a varredura primeiro."

    total_ativos = len(df_screener)
    altas = df_screener[df_screener["Var. Dia (%)"] > 0]
    baixas = df_screener[df_screener["Var. Dia (%)"] < 0]
    estaveis = df_screener[df_screener["Var. Dia (%)"] == 0]
    media_var = df_screener["Var. Dia (%)"].mean()

    # Filtros técnicos
    sobrevendidos = df_screener[df_screener["RSI (14)"] <= 35].sort_values(by="RSI (14)", ascending=True)
    sobrecomprados = df_screener[df_screener["RSI (14)"] >= 70].sort_values(by="RSI (14)", ascending=False)
    tendencia_alta = df_screener[df_screener["Sinal"].str.contains("Tendência de Alta", na=False)].sort_values(by="Vol. Relativo", ascending=False)
    volume_anormal = df_screener[df_screener["Vol. Relativo"] >= 1.5].sort_values(by="Vol. Relativo", ascending=False)
    top_scores = df_screener.sort_values(by=["Pontuação", "RSI (14)"], ascending=[False, True]).head(3)

    relatorio = []
    relatorio.append("### 📊 Relatório Quantitativo de Inteligência de Mercado\n")

    # 1. Panorama Geral
    if len(altas) > len(baixas) * 1.5:
        sentimento = "🟢 Forte Apetite a Risco (Mercado Altista)"
    elif len(baixas) > len(altas) * 1.5:
        sentimento = "🔴 Pressão Vendedora Predominante (Mercado Baixista)"
    else:
        sentimento = "🟡 Mercado Misto / Equilibrado"

    relatorio.append(f"**Termômetro do Dia:** {sentimento}")
    relatorio.append(f"- **Total de Ativos:** `{total_ativos}` | **Em Alta:** `{len(altas)}` | **Em Baixa:** `{len(baixas)}` | **Neutros:** `{len(estaveis)}`")
    relatorio.append(f"- **Variação Média da Carteira:** `{media_var:+.2f}%`\n")

    # 2. Oportunidades & Assimetria
    relatorio.append("#### 🎯 1. Oportunidades & Assimetria Favorável")
    if not sobrevendidos.empty:
        relatorio.append("**Ativos em Sobrevenda Extrema (Potencial de Repique):**")
        for _, row in sobrevendidos.iterrows():
            relatorio.append(
                f"- **{row['Ticker']}** ({row.get('Empresa', '')} - {row.get('Setor', '')}): "
                f"Preço `R$ {row['Preço (R$)']:.2f}` | RSI `{row['RSI (14)']}` | "
                f"Var. Dia `{row['Var. Dia (%)']:+.2f}%` | Vol. Relativo `{row['Vol. Relativo']:.2f}x`"
            )
    else:
        relatorio.append("- *Nenhum papel em zona crítica de sobrevenda (RSI ≤ 35) no fechamento atual.*")

    if not tendencia_alta.empty:
        relatorio.append("\n**Ativos em Estrutura de Alta Consolidada (Preço > Médias 20/50):**")
        for _, row in tendencia_alta.head(4).iterrows():
            relatorio.append(
                f"- **{row['Ticker']}** ({row.get('Empresa', '')}): `R$ {row['Preço (R$)']:.2f}` | "
                f"RSI `{row['RSI (14)']}` | Dist. SMA 20: `{row.get('Dist. SMA 20 (%)', 0):+.1f}%`"
            )

    # 3. Alertas de Risco
    relatorio.append("\n#### ⚠️ 2. Alertas de Risco & Cautela")
    tem_alertas = False
    if not sobrecomprados.empty:
        tem_alertas = True
        relatorio.append("**Ativos Sobrecomprados (Risco elevado de realização de lucros):**")
        for _, row in sobrecomprados.iterrows():
            relatorio.append(
                f"- **{row['Ticker']}**: RSI `{row['RSI (14)']}` | Preço `R$ {row['Preço (R$)']:.2f}` | Var: `{row['Var. Dia (%)']:+.2f}%`"
            )

    if not volume_anormal.empty:
        tem_alertas = True
        relatorio.append("\n**Atividade Institucional Anômala (Volume ≥ 1.5x a média de 20 dias):**")
        for _, row in volume_anormal.head(3).iterrows():
            fluxo = "Comprador 🟢" if row["Var. Dia (%)"] >= 0 else "Vendedor 🔴"
            relatorio.append(
                f"- **{row['Ticker']}**: Volume `{row['Vol. Relativo']:.2f}x` | Fluxo: {fluxo} (`{row['Var. Dia (%)']:+.2f}%`)"
            )

    if not tem_alertas:
        relatorio.append("- *Sem alertas severos de sobrecompra ou distorção de volume.*")

    # 4. Top Escolhas Quantitativas
    relatorio.append("\n#### 🏆 3. Top 3 Ativos Prioritários para Estudo Hoje")
    for i, (_, row) in enumerate(top_scores.iterrows(), 1):
        if row["RSI (14)"] <= 35:
            tese = "Gatilho de sobrevenda com assimetria positiva de risco/retorno"
        elif "Alta" in str(row.get("Sinal", "")):
            tese = "Continuidade de tendência compradora com suporte em médias"
        else:
            tese = "Equilíbrio técnico com momentum neutro/positivo"

        relatorio.append(
            f"{i}. **{row['Ticker']}** ({row.get('Empresa', '')}) — Score `{row['Pontuação']}`:\n"
            f"   - Preço: `R$ {row['Preço (R$)']:.2f}` | RSI: `{row['RSI (14)']}` | Vol. Relativo: `{row['Vol. Relativo']:.2f}x`\n"
            f"   - *Tese Técnica:* {tese}"
        )

    relatorio.append("\n---")
    relatorio.append("ℹ️ *Análise gerada 100% em Python com base nos modelos de Médias Móveis, Índice de Força Relativa (IFR/RSI) e Desvio Padrão de Volume.*")
    return "\n".join(relatorio)


def gerar_relatorio_gemini(df_screener: pd.DataFrame) -> str:
    """Envia o top do screener para o Gemini gerar uma síntese analítica (opcional)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ Chave de API `GEMINI_API_KEY` não configurada. Utilize a Análise em Python nativa que funciona instantaneamente sem chave."

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        df_top = df_screener.head(10)
        tabela_md = df_top.to_markdown(index=False)

        prompt = f"""
        Você é um especialista em análise quantitativa e fundamentalista de ações da B3.
        Abaixo estão as principais oportunidades identificadas pelo nosso Screener de Mercado:

        {tabela_md}

        Com base nestes dados, elabore um relatório executivo curto contendo:
        1. **Destaques do Dia**: Ativos mais promissores e por quê.
        2. **Avaliação de Risco**: Cuidados com ativos em zona de sobrevenda extrema ou volatilidade.
        3. **Sugestão Prática**: Priorização de estudo para o investidor hoje.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        return response.text
    except ImportError:
        return "⚠️ O pacote `google-genai` não está instalado no ambiente Python atual. Utilize a Análise em Python nativa."
    except Exception as e:
        return f"Erro ao consultar a API do Gemini: {e}"