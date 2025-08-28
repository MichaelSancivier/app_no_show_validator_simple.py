
import io
import re
import pandas as pd
import streamlit as st
from unidecode import unidecode

st.set_page_config(page_title="Validador No-show (1 columna)", layout="wide")
st.title("Validador de Máscaras — formato 1 columna")

st.markdown("""
Este app asume que **tanto la Exportación** como el **Catálogo de Reglas** vienen en **una sola columna** con el formato:
**`Causa. Motivo. Mascara...`**  
En el catálogo, la máscara es el **modelo** y usa `0` donde el prestador debe completar.
""")

# ------------------ Helpers ------------------
def norm(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s)
    s = unidecode(s).lower()
    s = re.sub(r"[.;:\\s]+$", "", s)  # quita puntuación final
    s = re.sub(r"\\s+", " ", s).strip()
    return s

def split_one_col(value: str):
    txt = re.sub(r"\\s+", " ", str(value)).strip()
    m = re.match(r"^(.*?\\.)\\s+(.*?\\.)\\s+(.*)$", txt)
    if m:
        causa = m.group(1).strip()
        motivo = m.group(2).strip()
        mascara = m.group(3).strip()
        return causa, motivo, mascara
    parts = [p.strip() for p in txt.split(".")]
    if len(parts) >= 3:
        causa = parts[0] + "."
        motivo = parts[1] + "."
        mascara = ".".join(parts[2:]).strip()
        return causa, motivo, mascara
    return "", "", txt

def template_to_regex(template: str):
    if pd.isna(template):
        template = ""
    t = re.sub(r"\\s+", " ", str(template)).strip()
    parts = re.split(r"0+", t)
    fixed = [re.escape(p) for p in parts]
    regex_body = r"(.+?)".join(fixed)
    regex_body = re.sub(r"\\ ", r"\\s+", regex_body)
    pattern = r"^\\s*" + regex_body + r"\\s*$"
    try:
        return re.compile(pattern, flags=re.IGNORECASE | re.DOTALL)
    except re.error:
        return re.compile(r"^\\s*" + re.escape(t) + r"\\s*$", flags=re.IGNORECASE)

# ------------------ Inputs ------------------
exp = st.file_uploader("Exportación del sistema (xlsx/csv) — UNA columna con Causa. Motivo. Mascara", type=["xlsx","csv"], key="exp")
rules = st.file_uploader("Catálogo de reglas (xlsx/csv) — UNA columna con Causa. Motivo. MascaraModelo", type=["xlsx","csv"], key="rules")

def read_any(file):
    if file is None:
        return None
    name = file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

if exp and rules:
    df_exp = read_any(exp)
    df_rules = read_any(rules)

    # Elegir columna si el archivo trae más de una
    col_exp = st.selectbox("Columna de la Exportación:", df_exp.columns, index=0, key="col_exp")
    col_rules = st.selectbox("Columna del Catálogo:", df_rules.columns, index=0, key="col_rules")

    # Construir mapa de reglas { (causa_norm, motivo_norm): regex }
    rule_map = {}
    for _, row in df_rules.iterrows():
        causa_m, motivo_m, modelo = split_one_col(row.get(col_rules, ""))
        key = (norm(causa_m), norm(motivo_m))
        rule_map[key] = template_to_regex(modelo)

    # Validar
    out = []
    for _, row in df_exp.iterrows():
        causa, motivo, mascara = split_one_col(row.get(col_exp, ""))
        key = (norm(causa), norm(motivo))
        regex = rule_map.get(key)
        texto = "" if pd.isna(mascara) else str(mascara)
        text_norm_spaces = re.sub(r"\\s+", " ", texto).strip()
        if regex and regex.fullmatch(text_norm_spaces):
            status = "Máscara correta"; detalle = ""
        else:
            contiene0 = re.search(r"(?:^|[\\s-])0(?:$|[\\s-.,;:])", text_norm_spaces)
            if not regex:
                detalle = "Sin modelo para este (Causa, Motivo)."
            else:
                detalle = "Contiene '0' sin completar." if contiene0 else "No coincide con el modelo."
            status = "No-show Técnico"
        out.append((causa, motivo, mascara, status, detalle))

    df_out = pd.DataFrame(out, columns=["Causa_extraida","Motivo_extraido","Mascara_extraida","ResultadoValidacao","DetalheValidacao"])
    # Adjuntamos la columna original para trazar
    df_out.insert(0, col_exp, df_exp[col_exp])

    st.success("Validación completa")
    st.dataframe(df_out, use_container_width=True)

    # Descargar Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_out.to_excel(writer, index=False, sheet_name="Resultado")
    st.download_button("Descargar Excel con resultado", data=output.getvalue(),
                       file_name="resultado_validacion_no_show.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       key="dl_excel")
else:
    st.info("Cargá la Exportación y el Catálogo para iniciar la validación.")
