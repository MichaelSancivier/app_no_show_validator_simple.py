
import io
import re
import unicodedata
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Validador de No-show (PT-BR)", layout="wide")
st.title("Validador de No-show — Entrada com muitas colunas (usa apenas 1)")

st.markdown("""
Este app **preserva todas as colunas** do arquivo de exportação e **adiciona apenas 1 coluna nova** com o resultado:
**`Classificação No-show`** → "Máscara correta" ou "No-show Técnico".

### Como funciona
- Seu **arquivo de exportação** pode ter **muitas colunas**; você irá **escolher qual coluna** contém o texto **"Causa. Motivo. Mascara..."**.
- O **catálogo de regras** é **1 coluna** no mesmo formato **"Causa. Motivo. MascaraModelo"** (com `0` como campos a serem preenchidos).
- O algoritmo **só considera** essa coluna de texto (Causa+Motivo+Mascara). **Todo o resto é ignorado** para a validação.
""")

# ------------------ Funções auxiliares ------------------
def remove_acentos(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def norm(s: str) -> str:
    """Normalização robusta para comparar Causa/Motivo entre exportação e catálogo."""
    if pd.isna(s):
        return ""
    s = str(s)
    s = remove_acentos(s).lower()
    s = re.sub(r"[.;:\\s]+$", "", s)  # remove pontuação final
    s = re.sub(r"\\s+", " ", s).strip()
    return s

def dividir_texto_uma_coluna(value: str):
    """
    Divide o texto no padrão 'Causa. Motivo. Mascara...' em 3 partes.
    Retorna (causa, motivo, mascara). Se não conseguir, devolve tudo em 'mascara'.
    """
    txt = re.sub(r"\\s+", " ", str(value)).strip()
    m = re.match(r"^(.*?\\.)\\s+(.*?\\.)\\s+(.*)$", txt)
    if m:
        causa = m.group(1).strip()
        motivo = m.group(2).strip()
        mascara = m.group(3).strip()
        return causa, motivo, mascara
    partes = [p.strip() for p in txt.split(".")]
    if len(partes) >= 3:
        causa = partes[0] + "."
        motivo = partes[1] + "."
        mascara = ".".join(partes[2:]).strip()
        return causa, motivo, mascara
    return "", "", txt

def modelo_para_regex(template: str):
    """
    Converte a máscara modelo (com '0' como placeholder) em uma regex ancorada.
    - Cada sequência de '0' vira um coringa '(.+?)' (não guloso).
    - Trechos fixos são exigidos literalmente (permitindo variação de espaços).
    """
    if pd.isna(template):
        template = ""
    t = re.sub(r"\\s+", " ", str(template)).strip()
    partes = re.split(r"0+", t)
    fixos = [re.escape(p) for p in partes]
    corpo = r"(.+?)".join(fixos)
    corpo = re.sub(r"\\ ", r"\\s+", corpo)
    padrao = r"^\\s*" + corpo + r"\\s*$"
    try:
        return re.compile(padrao, flags=re.IGNORECASE | re.DOTALL)
    except re.error:
        return re.compile(r"^\\s*" + re.escape(t) + r"\\s*$", flags=re.IGNORECASE)

# ------------------ Entradas ------------------
arq_exp = st.file_uploader("Exportação (xlsx/csv) — contém muitas colunas", type=["xlsx","csv"], key="exp")
arq_regras = st.file_uploader("Catálogo de Regras (xlsx/csv) — 1 coluna: 'Causa. Motivo. MascaraModelo'", type=["xlsx","csv"], key="rules")

def ler_arquivo(f):
    if f is None:
        return None
    nome = f.name.lower()
    if nome.endswith(".csv"):
        return pd.read_csv(f)
    return pd.read_excel(f)

if arq_exp and arq_regras:
    df_exp = ler_arquivo(arq_exp)
    df_reg = ler_arquivo(arq_regras)

    col_exp = st.selectbox("Escolha a coluna da exportação que contém 'Causa. Motivo. Mascara...':",
                           df_exp.columns, index=0, key="col_exp")
    col_reg = st.selectbox("Escolha a coluna do catálogo (1 coluna com 'Causa. Motivo. MascaraModelo'):",
                           df_reg.columns, index=0, key="col_reg")

    # Mapa de regras: {(causa_norm, motivo_norm): regex_mascara_modelo}
    mapa = {}
    for _, row in df_reg.iterrows():
        causa_m, motivo_m, modelo = dividir_texto_uma_coluna(row.get(col_reg, ""))
        chave = (norm(causa_m), norm(motivo_m))
        mapa[chave] = modelo_para_regex(modelo)

    # Validação linha a linha — usa SOMENTE a coluna escolhida
    resultados = []
    for _, row in df_exp.iterrows():
        texto = row.get(col_exp, "")
        causa, motivo, mascara_preenchida = dividir_texto_uma_coluna(texto)
        chave = (norm(causa), norm(motivo))
        regex = mapa.get(chave)
        mascara_norm = re.sub(r"\\s+", " ", str(mascara_preenchida)).strip()

        if regex and regex.fullmatch(mascara_norm):
            resultados.append("Máscara correta")
        else:
            resultados.append("No-show Técnico")

    # Saída: mantém todas as colunas originais + 1 coluna nova
    df_saida = df_exp.copy()
    df_saida["Classificação No-show"] = resultados

    st.success("Validação concluída!")
    st.dataframe(df_saida, use_container_width=True)

    # Download Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_saida.to_excel(writer, index=False, sheet_name="Resultado")
    st.download_button("Baixar Excel com 'Classificação No-show'",
                       data=buffer.getvalue(),
                       file_name="resultado_no_show.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       key="dl_excel")
else:
    st.info("Envie a exportação e o catálogo de regras para iniciar.")
