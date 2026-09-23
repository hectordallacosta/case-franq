import pandas as pd
import numpy as np

# ============================================================================
# PARTE 1 — Extração e amostragem estratificada por grade (~100k linhas)
# ============================================================================

# ajuste o caminho pro csv extraído
caminho = r"C:\Users\hector.dallacosta\Documents\Dataset_keagle\accepted_2007_to_2018q4.csv\ARQUIVO.csv"

# colunas relevantes pro teste (evita estourar memória lendo tudo)
# obs: adicionei "addr_state" pra dar pra usar como filtro de estado no
# dashboard, como sugerido antes — se não quiser, pode remover essa linha.
colunas = [
    "id", "loan_amnt", "term", "int_rate", "installment", "grade", "sub_grade",
    "emp_length", "home_ownership", "annual_inc", "verification_status",
    "issue_d", "loan_status", "purpose", "dti", "delinq_2yrs",
    "open_acc", "pub_rec", "revol_bal", "revol_util", "total_acc",
    "application_type", "fico_range_low", "fico_range_high", "addr_state",
]

df = pd.read_csv(caminho, usecols=colunas, low_memory=False)

# issue_d vem tipo "Dec-2018" -> converter pra data
df["issue_d"] = pd.to_datetime(df["issue_d"], format="%b-%Y")

# pega só os 2 últimos anos disponíveis no dataset
data_corte = df["issue_d"].max() - pd.DateOffset(years=2)
df = df[df["issue_d"] >= data_corte]

# amostra representativa de ~100k, estratificada por grade
amostra = df.groupby("grade", group_keys=False).apply(
    lambda x: x.sample(frac=min(1, 100_000 / len(df)), random_state=42),
    include_groups=False,
)
# include_groups=False remove a coluna "grade" do resultado do apply (some
# versões do pandas duplicam/derrubam a coluna de agrupamento) — por isso
# reconstruímos o df da amostra usando os índices originais, que preservam
# todas as colunas certinho:
amostra = df.loc[amostra.index].copy()

amostra.to_csv("lending_club_amostra.csv", index=False)
print("Amostra bruta:", amostra.shape)
print(amostra["grade"].value_counts())

# >>> aqui está a costura que faltava: a amostra vira a base de trabalho <<<
df = amostra.copy()

# ============================================================================
# PARTE 2 — Preparação de campos para o dashboard Looker Studio
# ============================================================================

# --- 1) Flag de inadimplência ----------------------------------------------
# Critério: "Charged Off" e "Default" são inadimplência consolidada.
# "Late (31-120 days)" também entra porque já é atraso relevante (>30 dias).
# Deixe esse critério explícito no dashboard — é parte do "self-service
# thinking": o usuário de negócio precisa saber o que está sendo contado
# como inadimplente sem perguntar pro time de dados.
STATUS_INADIMPLENTE = ["Charged Off", "Default", "Late (31-120 days)"]

df["inadimplente"] = df["loan_status"].isin(STATUS_INADIMPLENTE).astype(int)

def agrupar_status(status):
    if status == "Fully Paid":
        return "Quitado"
    if status == "Current":
        return "Em dia"
    if status in STATUS_INADIMPLENTE:
        return "Inadimplente"
    return "Outro"

df["status_carteira"] = df["loan_status"].apply(agrupar_status)

# --- 2) Datas: ano_mes para séries temporais --------------------------------
df["ano_mes"] = df["issue_d"].dt.to_period("M").dt.to_timestamp()
df["ano"] = df["issue_d"].dt.year

# --- 3) Faixas de renda e de DTI --------------------------------------------
bins_renda = [0, 30000, 50000, 75000, 100000, 150000, np.inf]
labels_renda = ["até 30k", "30k-50k", "50k-75k", "75k-100k", "100k-150k", "150k+"]
df["faixa_renda"] = pd.cut(df["annual_inc"], bins=bins_renda, labels=labels_renda)

bins_dti = [-0.01, 10, 20, 30, 40, np.inf]
# rótulos com "a" em vez de hífen: o Excel em pt-BR converte "10-20" em data
# (vira "out/20") se alguém abrir o CSV
labels_dti = ["0 a 10", "10 a 20", "20 a 30", "30 a 40", "40+"]
df["faixa_dti"] = pd.cut(df["dti"], bins=bins_dti, labels=labels_dti)

# --- 4) Prazo (term) limpo ---------------------------------------------------
df["term_meses"] = df["term"].astype(str).str.extract(r"(\d+)").astype(float)

# --- 5) Renomear pra nomes de negócio ----------------------------------------
RENOMEAR = {
    "loan_amnt": "valor_emprestimo",
    "int_rate": "taxa_juros",
    "installment": "parcela",
    "annual_inc": "renda_anual",
    "purpose": "finalidade",
    "addr_state": "estado",
    "verification_status": "status_verificacao",
    "home_ownership": "moradia",
}
df = df.rename(columns=RENOMEAR)

# --- 6) Seleção final de colunas ---------------------------------------------
colunas_finais = [
    "id", "issue_d", "ano_mes", "ano",
    "valor_emprestimo", "taxa_juros", "parcela", "term_meses",
    "grade", "sub_grade",
    "renda_anual", "faixa_renda", "dti", "faixa_dti",
    "finalidade", "estado", "status_verificacao", "moradia",
    "loan_status", "status_carteira", "inadimplente",
]
colunas_finais = [c for c in colunas_finais if c in df.columns]

df_final = df[colunas_finais].copy()

# --- 7) Exportar --------------------------------------------------------------
# Formato brasileiro (separador ";" e decimal ","). Com decimal ".", o Looker
# em pt-BR lê valores como "15.05" (taxa_juros) ou "20.05" (dti) como DATA
# (15 de maio) e os descarta — a média de juros caía de 13,00% para 12,83%.
# Datas também vão já formatadas como dd/mm/aaaa.
df_final["issue_d"] = df_final["issue_d"].dt.strftime("%d/%m/%Y")
df_final["ano_mes"] = df_final["ano_mes"].dt.strftime("%d/%m/%Y")
df_final.to_csv(
    "base_looker_finlend.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig"
)
print("\nBase final para o Looker:", df_final.shape)
print(df_final.head())
