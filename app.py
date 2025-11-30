import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO

st.title("📊 Plataforma de Balanceamento de Linha Assistida por IA")

st.subheader("1. Entrada de Dados")

st.write("Insira a lista de tarefas seguindo o formato sugerido:")

with st.expander("Cadastrar Tarefas"):
    tarefas = st.text_area(
        "Formato: Tarefa,Tempo,Precedência (use '-' se não houver). Separe múltiplas precedências com ';'",
        "A,10,-\nB,7,A\nC,6,A\nD,5,B;C"
    )

demanda = st.number_input("Demanda diária", min_value=1, value=100)
tempo_disp = st.number_input("Tempo disponível por turno (minutos)", min_value=1, value=480)

# Processamento dos dados
linhas = [l.split(",") for l in tarefas.split("\n") if l.strip()]
df = pd.DataFrame(linhas, columns=["Tarefa","Tempo","Precedencia"])
df["Tempo"] = df["Tempo"].astype(float)

# Cálculo do Takt Time
takt = tempo_disp / demanda
st.subheader("2. Cálculos Automáticos")
st.write(f"**Takt Time = {takt:.2f} min/ciclo**")

# Estações mínimas teóricas
n_min = df["Tempo"].sum() / takt
st.write(f"**Nº Mínimo Teórico de Estações: {n_min:.2f}**")

# Montar diagrama de precedência
st.subheader("Diagrama de Precedência (GBO)")
G = nx.DiGraph()

for _, row in df.iterrows():
    G.add_node(row["Tarefa"])
    if row["Precedencia"] != "-":
        for p in row["Precedencia"].split(";"):
            G.add_edge(p.strip(), row["Tarefa"])

plt.figure(figsize=(8,6))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=2000, font_size=12)
buf = BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)
st.image(buf)

# Sugestão de agrupamento (heurística simplificada)
st.subheader("3. Sugestão de Balanceamento de Estações")

tarefas_ord = df.sort_values(by="Tempo", ascending=False)
ws = []
estacao = []
tempo_estacao = 0

for _, row in tarefas_ord.iterrows():
    if tempo_estacao + row["Tempo"] <= takt:
        estacao.append(row["Tarefa"])
        tempo_estacao += row["Tempo"]
    else:
        ws.append((estacao, tempo_estacao))
        estacao = [row["Tarefa"]]
        tempo_estacao = row["Tempo"]

ws.append((estacao, tempo_estacao))

for i, (t, tm) in enumerate(ws):
    cor = "🔴" if tm > takt*0.95 else "🟢"
    st.write(f"**WS {i+1}: {t} — Tempo total: {tm:.2f} {cor}**")

# Eficiência da linha
ef = df["Tempo"].sum() / (len(ws) * takt)
st.subheader("Eficiência da Linha")
st.write(f"**Eficiência = {ef*100:.2f}%**")
