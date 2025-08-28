# Validador de No-show

Aplicação **Streamlit** para validar **Máscaras de No-show** em ordens de serviço.  
Funciona com **exportações do sistema com muitas colunas**, mas considera apenas **uma coluna** escolhida pelo usuário que contém o texto no formato:

Causa. Motivo. Mascara...

O catálogo de regras deve vir em **uma coluna** também no mesmo formato, mas com `0` nos pontos que devem ser preenchidos.

---

## ⚙️ Como funciona

1. Faça upload da **Exportação** (arquivo Excel/CSV) que contém muitas colunas.  
   - Você escolherá qual coluna tem o texto `Causa. Motivo. Mascara...`.

2. Faça upload do **Catálogo de Regras** (Excel/CSV, **1 coluna**) com os modelos:  
   - Exemplo:  
     Agendamento cancelado. Cancelada a Pedido do Cliente. Cliente 0, contato via 0 em 0 - 0, informou indisponibilidade para o atendimento.

3. A aplicação valida **somente essa coluna**.  
   - Se a máscara está de acordo com o modelo → `Máscara correta`  
   - Caso contrário (não preencheu, não bate com o modelo ou não existe modelo) → `No-show Técnico`

4. O arquivo de saída mantém **todas as colunas originais** + **1 nova coluna**:  
   - `Classificação No-show`

---

## 🖥️ Rodar localmente

Clone este repositório e instale as dependências:

pip install -r requirements.txt

Inicie a aplicação:

streamlit run app_validacao_no_show_ptbr.py

---

## ☁️ Deploy no Streamlit Cloud

1. Vá até Streamlit Cloud (https://share.streamlit.io).  
2. Conecte sua conta GitHub e escolha este repositório.  
3. Configure:
   - Branch: main
   - Main file path: app_validacao_no_show_ptbr.py
4. Clique em Deploy 🚀

A aplicação ficará disponível em uma URL pública que você pode compartilhar com a equipe.

---

## 📂 Estrutura esperada dos arquivos

### Exportação (entrada com muitas colunas)
| O.S. | MOTIVO CANCELAMENTO | ... | ColunaSelecionada | ... |
|------|---------------------|-----|-------------------|-----|
| 92171 | Problema técnico | ... | Agendamento cancelado. Cancelada a Pedido do Cliente. Cliente João ... | ... |

### Catálogo de Regras (1 coluna)
| Regras |
|--------|
| Agendamento cancelado. Cancelada a Pedido do Cliente. Cliente 0, contato via 0 em 0 - 0, informou indisponibilidade para o atendimento. |
| Agendamento cancelado. Erro de Agendamento - OS Agendada Incorretamente (tipo/motivo/produto). OS apresentou erro de 0 identificado via 0. Contato com cliente 0 - em 0 - 0 |
| ... |

---

## 📤 Saída gerada

O arquivo final é igual ao da exportação original, mas com uma coluna adicional no fim:

| ... | ColunaSelecionada | ... | Classificação No-show |
|-----|-------------------|-----|-----------------------|
| ... | Agendamento cancelado. Cancelada a Pedido do Cliente. Cliente João ... | ... | Máscara correta |
| ... | Agendamento cancelado. Erro de Agendamento - OS ... | ... | No-show Técnico |

---
