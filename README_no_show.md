
# Validador de Máscaras (No-show Técnico)

App em Streamlit para validar se a **Máscara** preenchida por um prestador está correta para o respectivo par **Causa + Motivo**.

## Como funciona
- Você fornece **dois arquivos**:
  1. **Exportação do sistema** com as colunas: `Causa`, `Motivo`, `Mascara` (preenchida).
  2. **Catálogo/Regras** com as colunas: `Causa`, `Motivo`, `MascaraModelo` (o texto base com `0` nos pontos que o prestador deve preencher).
- Para cada linha da exportação:
  - Procuramos o par `(Causa, Motivo)` nas regras.
  - Convertimos a `MascaraModelo` em uma **regex**: cada `0` vira um coringa `(.+?)` e o restante do texto precisa bater.
  - Se a `Mascara` *casa* com o modelo, marcamos **"Máscara correta"**; caso contrário, **"No-show Técnico"**.

> Observação: Apenas **Causa, Motivo, Mascara** são usados. Outros campos (nome, canal, data, hora etc.) **não** são considerados.

## Rodando localmente

### 1) Criar um virtualenv e instalar dependências
```bash
pip install -r requirements.txt
```

### 2) Iniciar
```bash
streamlit run app_no_show_validator.py
```

## Dicas
- Garanta que os textos de `Causa` e `Motivo` nos dois arquivos estejam coerentes (acentos, maiúsculas/minúsculas). O app normaliza para comparar (minúsculas, sem acentos, espaços colapsados), então pequenas variações são toleradas.
- O app acusa quando a máscara preenchida **ainda contém '0'**, o que indica não preenchimento.
- O Excel de saída terá duas colunas novas: `ResultadoValidacao` e `DetalheValidacao`.
