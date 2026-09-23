# Teste Técnico — Analista de Dados Pleno (FinLend / Lending Club)

Análise da carteira de crédito P2P da FinLend (fintech fictícia do case), usando o
dataset público **Lending Club Loan Data**. O teste tem três partes, cada uma
correspondendo a uma competência da vaga.

## Contexto

A FinLend enfrenta três desafios:

1. Áreas de negócio sem autonomia para consultar dados (tudo vira ticket).
2. Inadimplência subindo sem explicação estatística clara.
3. Um agente de IA (LLM) que responde sobre a carteira e precisa ser validado.

## Estrutura do repositório

| Arquivo | Descrição |
|---|---|
| `parte2_executado.ipynb` | **Parte 2** — Notebook de análise estatística da inadimplência (EDA, teste de hipótese, insight não-óbvio e recomendação), com os resultados já renderizados. |
| `extracao_e_preparacao_looker.py` | Script de extração e preparação da amostra (~100k registros estratificados por *grade*, safras 2016–2018) a partir do dataset bruto do Kaggle. Gera o CSV usado nas análises. |
| `base_looker_finlend.csv` | Amostra tratada (~100k linhas) usada pelo notebook e pelo dashboard. Separador `;`, decimal `,` (formato pt-BR). |
| `requirements.txt` | Dependências Python para rodar o notebook. |

## Parte 1 — Dashboard (Looker Studio)

Dashboard de acompanhamento da carteira, com visão geral, indicadores de
inadimplência, filtros interativos e um elemento de *self-service* (drill-down
*grade → sub-grade*).

🔗 **Link:** _(inserir o link de compartilhamento do Looker Studio aqui)_

## Parte 2 — Análise estatística (Python)

Principais achados:

- **Hipótese do Head de Risco** ("a inadimplência sobe porque aprovamos muito D/E")
  testada e **decomposta em duas afirmações**: D/E são de fato mais arriscados
  (χ², p < 0,001), **mas** sua participação na carteira *caiu* (de ~21% para ~18%) —
  então não explicam um aumento agregado.
- **Insight não-óbvio:** a taxa de inadimplência crua *parece* despencar ao longo do
  tempo, mas isso é **viés de maturação de safra** — 86% dos empréstimos de 2018 ainda
  estão em curso e não tiveram tempo de inadimplir. A leitura correta exige análise de
  safra (*vintage*).

## Parte 3 — Validação de IA generativa

_(a desenvolver)_ Validação quantitativa e qualitativa das respostas do agente de IA
sobre a carteira, com proposta de processo recorrente de validação.

## Como reproduzir

```bash
pip install -r requirements.txt
jupyter notebook parte2_executado.ipynb
```

O notebook lê `base_looker_finlend.csv` da mesma pasta.

---

> **Uso de IA assistiva:** conforme permitido no enunciado, um assistente de IA foi
> usado para acelerar a escrita de código e revisar o raciocínio estatístico. As
> decisões analíticas e conclusões foram validadas contra os dados.
