"""Painel Streamlit — Mapeamento Eleitoral 2026, São João del-Rei (MG).
"""
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent
NOTEBOOK = RAIZ / "sjdr.ipynb"
DIR_PROC = RAIZ / "dados_processados"
DIR_MAPAS = RAIZ / "mapas_html"

ARQUIVOS_NECESSARIOS = [
    DIR_PROC / "sjdr_resumo_1t.csv",
    DIR_PROC / "sjdr_resumo_2t.csv",
    DIR_PROC / "sjdr_locais_1t.csv",
    DIR_PROC / "sjdr_locais_2t.csv",
    DIR_MAPAS / "mapa_1t_cand1.html",
    DIR_MAPAS / "mapa_1t_cand2.html",
    DIR_MAPAS / "mapa_2t_comparativo.html",
]

st.set_page_config(page_title="Mapa Eleitoral 2026 - São João del-Rei", page_icon="🗳️", layout="wide")


def executar_notebook():
    import nbformat
    from jupyter_client import KernelManager
    from jupyter_client.kernelspec import KernelSpecManager
    from nbclient import NotebookClient

    ksm = KernelSpecManager()
    ksm.kernel_dirs = []  # usa só o kernel nativo -> o Python deste ambiente conda
    km = KernelManager(kernel_name="python3", kernel_spec_manager=ksm)
    nb = nbformat.read(NOTEBOOK, as_version=4)
    NotebookClient(nb, km=km, timeout=3600, resources={"metadata": {"path": str(RAIZ)}}).execute()
    nbformat.write(nb, NOTEBOOK)


# No Streamlit Community Cloud o repositório fica em /mount/src: lá os dados e mapas já
# vêm prontos do GitHub, então o botão de reprocessar só aparece na execução local.
NA_NUVEM = str(RAIZ).startswith("/mount/src")

faltando = [p.name for p in ARQUIVOS_NECESSARIOS if not p.exists()]
reprocessar = False if NA_NUVEM else st.sidebar.button(
    "🔄 Reprocessar (executar notebook)", help="Executa sjdr.ipynb novamente")
if faltando or reprocessar:
    motivo = f"arquivos ausentes: {', '.join(faltando)}" if faltando else "solicitado pelo usuário"
    with st.spinner(f"Executando o notebook sjdr.ipynb ({motivo})... pode levar alguns minutos."):
        executar_notebook()
    st.cache_data.clear()
    st.toast("Notebook executado, dados e mapas atualizados.")


@st.cache_data
def carregar_tabelas():
    ler = lambda nome: pd.read_csv(DIR_PROC / nome, dtype={"NR_ZONA": str, "NR_LOCAL_VOTACAO": str, "id_local": str})
    return (ler("sjdr_resumo_1t.csv"), ler("sjdr_resumo_2t.csv"),
            ler("sjdr_locais_1t.csv"), ler("sjdr_locais_2t.csv"))


res_1t, res_2t, loc_1t, loc_2t = carregar_tabelas()
c1_num, c2_num = res_2t["NR_VOTAVEL"].iloc[:2].tolist()
c1_nome, c2_nome = res_2t["NM_VOTAVEL"].iloc[:2].tolist()
fmt = lambda n: f"{int(n):,}".replace(",", ".")
pct = lambda x: f"{x:.2f}%".replace(".", ",")

# ----------------------------------------------------------------------------
# Seleção do mapa (define o turno exibido no cabeçalho)
MAPAS = {
    f"1º turno — {c1_nome}": dict(
        turno=1, arquivo="mapa_1t_cand1.html",
        fato=f"{c1_nome} venceu o 1º turno com {pct(res_1t.iloc[0]['PCT_VALIDOS'])} e liderou em "
             f"{(loc_1t['lider_1t'] == c1_nome).sum()} de {len(loc_1t)} prédios. Seus maiores percentuais estão nos "
             "bairros fora do núcleo central (Matosinhos, Jardim Paulo Campos, COHAB) e nas colônias rurais.",
        design="Paleta sequencial `YlGnBu` (verde e amarelo da campanha até o azul do PL), 7 classes fixas "
               "(0–35, 35–40, …, 60–100%), iguais às do mapa de Lula, opacidade 0,65 sobre base cinza, tooltip "
               "HTML com o líder do local e círculos proporcionais aos votos.",
    ),
    f"1º turno — {c2_nome}": dict(
        turno=1, arquivo="mapa_1t_cand2.html",
        fato=f"{c2_nome} teve {pct(res_1t.iloc[1]['PCT_VALIDOS'])} e liderou em {(loc_1t['lider_1t'] == c2_nome).sum()} "
             "prédios, concentrados no arco de bairros populares em torno do centro (Senhor dos Montes, Alto das "
             "Mercês, São Geraldo), no Distrito do Rio das Mortes, no Tejuco e no Campus Dom Bosco da UFSJ.",
        design="Paleta sequencial `Reds` (vermelho do PT), com as mesmas 7 classes e a mesma opacidade do mapa "
               "anterior para permitir a comparação direta entre os candidatos.",
    ),
    "2º turno — comparativo (saldo Flávio − Lula)": dict(
        turno=2, arquivo="mapa_2t_comparativo.html",
        fato=f"Disputa decidida por {fmt(res_2t.iloc[0]['QT_VOTOS'] - res_2t.iloc[1]['QT_VOTOS'])} votos. Lula cresceu "
             f"~8 p.p. sobre o 1º turno e virou 9 locais, mas {c1_nome} manteve os bairros urbanos fora do centro e a "
             f"zona rural. Placar por prédio: {(loc_2t['lider_2t'] == c1_nome).sum()} × "
             f"{(loc_2t['lider_2t'] == c2_nome).sum()}, com {(loc_2t['lider_2t'] == 'EMPATE').sum()} empates.",
        design="Paleta divergente `RdBu` com classes simétricas em torno de 0 (−100, −30, −15, −5, 0, 5, 15, 30, "
               "100 p.p.): vermelho para Lula e azul para Flávio. `LayerControl` alterna entre as áreas de influência "
               "(Voronoi) e os pontos exatos do TSE, que têm popup.",
    ),
}

st.sidebar.header("Mapa temático")
escolha = st.sidebar.radio("Selecione o mapa:", list(MAPAS))
mapa = MAPAS[escolha]
turno = mapa["turno"]
res = res_1t if turno == 1 else res_2t
loc = loc_1t if turno == 1 else loc_2t

# ----------------------------------------------------------------------------
# Cabeçalho (acompanha o turno do mapa selecionado)
st.title("🗳️ Mapeamento Eleitoral Geoespacial — São João del-Rei (MG)")
st.caption("Ferramentas para Data Science — DCOMP/UFSJ · Fonte: TSE (boletins de urna e locais de votação) "
           "e IBGE (malha municipal) · Eleição presidencial 2026")

st.markdown(f"#### Resultado do {turno}º turno no município")
a, b = res.iloc[0], res.iloc[1]
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"1º lugar — {a['NM_VOTAVEL']}", f"{fmt(a['QT_VOTOS'])} votos",
            f"{pct(a['PCT_VALIDOS'])} dos válidos", delta_color="off")
col2.metric(f"2º lugar — {b['NM_VOTAVEL']}", f"{fmt(b['QT_VOTOS'])} votos",
            f"{pct(b['PCT_VALIDOS'])} dos válidos", delta_color="off")
col3.metric("Diferença entre 1º e 2º", f"{fmt(a['QT_VOTOS'] - b['QT_VOTOS'])} votos",
            f"{(a['PCT_VALIDOS'] - b['PCT_VALIDOS']):.2f}".replace(".", ",") + " p.p.", delta_color="off")
if turno == 1:
    outros = res.iloc[2:]
    col4.metric("Demais candidatos", f"{fmt(outros['QT_VOTOS'].sum())} votos",
                f"{pct(outros['PCT_VALIDOS'].sum())} · 3º: {res.iloc[2]['NM_VOTAVEL']}", delta_color="off")
else:
    col4.metric("Locais vencidos (prédios)",
                f"{(loc['lider_2t'] == c1_nome).sum()} × {(loc['lider_2t'] == c2_nome).sum()}",
                f"{c1_nome.split()[0]} × {c2_nome.split()[0]} · {(loc['lider_2t'] == 'EMPATE').sum()} empates",
                delta_color="off")

st.divider()

# ----------------------------------------------------------------------------
st.subheader(escolha)
st.iframe(DIR_MAPAS / mapa["arquivo"], height=650)
c_fato, c_design = st.columns(2)
c_fato.info(f"**O fato.** {mapa['fato']}")
c_design.success(f"**O design.** {mapa['design']}")
st.caption("Relatório completo (fato e design de cada mapa) no notebook `sjdr.ipynb`. "
           "Áreas de influência = polígonos de Voronoi a partir das coordenadas oficiais dos locais de votação.")

st.divider()

# ----------------------------------------------------------------------------
st.subheader("📊 Resultado por região")
nums = [c1_num, c2_num]


def por_regiao(df, suf):
    g = df.groupby("regiao")[[f"votos_{n}" for n in nums] + [f"total_validos_{suf}"]].sum()
    return pd.DataFrame({f"% {res_2t.iloc[i]['NM_VOTAVEL']}": (g[f"votos_{n}"] / g[f"total_validos_{suf}"] * 100).round(1)
                         for i, n in enumerate(nums)})


r1, r2 = st.columns(2)
r1.markdown("**1º turno** (% dos votos válidos)")
r1.bar_chart(por_regiao(loc_1t, "1t"), horizontal=True, stack=False, color=["#2166ac", "#b2182b"])
r2.markdown("**2º turno** (% dos votos válidos)")
r2.bar_chart(por_regiao(loc_2t, "2t"), horizontal=True, stack=False, color=["#2166ac", "#b2182b"])

st.subheader("📋 Detalhamento por local de votação (TSE)")
f1, f2 = st.columns(2)
regioes = f1.multiselect("Região", sorted(loc_2t["regiao"].unique()), default=sorted(loc_2t["regiao"].unique()))
bairro = f2.selectbox("Bairro", ["Todos"] + sorted(loc_2t["NM_BAIRRO"].dropna().unique()))

tab = loc_2t.merge(loc_1t[["id_local", "lider_1t", f"pct_{c1_num}_1t", f"pct_{c2_num}_1t"]], on="id_local")
tab = tab[tab["regiao"].isin(regioes)]
if bairro != "Todos":
    tab = tab[tab["NM_BAIRRO"] == bairro]

st.dataframe(
    tab[["NM_LOCAL_VOTACAO", "NM_BAIRRO", "regiao", "QTD_SECOES", "LISTA_SECOES",
         f"pct_{c1_num}_1t", f"pct_{c2_num}_1t", "lider_1t",
         f"pct_{c1_num}_2t", f"pct_{c2_num}_2t", "saldo_pct", "lider_2t"]]
    .sort_values("saldo_pct", ascending=False),
    width="stretch", hide_index=True,
    column_config={
        "NM_LOCAL_VOTACAO": "Local de votação", "NM_BAIRRO": "Bairro", "regiao": "Região",
        "QTD_SECOES": "Seções", "LISTA_SECOES": "Lista de seções",
        f"pct_{c1_num}_1t": st.column_config.NumberColumn(f"% {c1_nome} 1T", format="%.1f"),
        f"pct_{c2_num}_1t": st.column_config.NumberColumn(f"% {c2_nome} 1T", format="%.1f"),
        "lider_1t": "Líder 1T",
        f"pct_{c1_num}_2t": st.column_config.NumberColumn(f"% {c1_nome} 2T", format="%.1f"),
        f"pct_{c2_num}_2t": st.column_config.NumberColumn(f"% {c2_nome} 2T", format="%.1f"),
        "saldo_pct": st.column_config.NumberColumn("Saldo 2T (p.p.)", format="%+.1f",
                                                   help=f"% {c1_nome} − % {c2_nome}"),
        "lider_2t": "Líder 2T",
    },
)

with st.expander("Resultado completo do 1º turno no município"):
    st.dataframe(res_1t, hide_index=True, width="stretch")
