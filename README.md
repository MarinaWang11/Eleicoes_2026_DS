# Mapeamento Eleitoral 2026 — São João del-Rei (MG)

Atividade prática "Mapeamento Eleitoral e Visualização Geoespacial com Folium"
Tecnologias para Data Science — DCOMP/UFSJ — Prof.ª Carolina Xavier

Distribuição espacial dos votos para Presidente (1º e 2º turnos de 2026) por local de votação e seção eleitoral em São João del-Rei, com `pandas`, `geopandas`, `folium` e um painel em `streamlit`.

## Resultados

| Turno | Flávio Bolsonaro (PL) | Lula (PT) | Outros |
|---|---|---|---|
| 1º | 25.618 (48,95%) | 21.946 (41,94%) | 4.768 (9,11%) |
| 2º | 27.777 (50,12%) | 27.644 (49,88%) | — |

Diferença no 2º turno: 133 votos.

### Mapas interativos (`mapas_html/`)
| Arquivo | Conteúdo |
|---|---|
| [`mapa_1t_cand1.html`](mapas_html/mapa_1t_cand1.html) | 1º turno — % de Flávio Bolsonaro por local (paleta sequencial `YlGnBu`) |
| [`mapa_1t_cand2.html`](mapas_html/mapa_1t_cand2.html) | 1º turno — % de Lula por local (paleta sequencial `Reds`) |
| [`mapa_2t_comparativo.html`](mapas_html/mapa_2t_comparativo.html) | 2º turno — saldo Flávio − Lula (paleta divergente `RdBu` centrada em 0) + `LayerControl` |

Para abrir, baixe o arquivo e abra no navegador. O relatório com o fato e o design de cada mapa está no notebook [`sjdr.ipynb`](sjdr.ipynb).

## Como executar

```bash
conda env create -f environment.yml
conda activate eleicao_sjdr

streamlit run app_sjdr.py     
```

## Estrutura

```
Eleicao/
├── sjdr.ipynb             # tratamento dos dados do TSE, mapas folium e relatório (Markdown)
├── app_sjdr.py            # painel Streamlit (executa o notebook se necessário)
├── environment.yml        # ambiente conda com versões exatas
├── dados_brutos/          # recorte bruto (sem transformação) de São João del-Rei
│   ├── bweb_1t_sjdr.csv           # boletim de urna, 1º turno, cargo Presidente
│   ├── bweb_2t_sjdr.csv           # boletim de urna, 2º turno, cargo Presidente
│   ├── locais_sjdr.csv            # eleitorado por local de votação (lat/long)
│   └── malha_sjdr_ibge.geojson    # contorno do município (IBGE)
├── dados_processados/     # votos agregados por local, resumos e áreas de Voronoi
└── mapas_html/            # mapas interativos exportados
```

## Dados de origem

Os arquivos originais do TSE para Minas Gerais não estão no repositório. O notebook só precisa deles se algum arquivo de `dados_brutos/` estiver faltando. Nesse caso, baixe-os do [Portal de Dados Abertos do TSE](https://dadosabertos.tse.jus.br/) e coloque-os nesta pasta:

| Arquivo | Conjunto de dados no portal do TSE |
|---|---|
| `bweb_1t_MG_051020261403.csv` | Resultados 2026 — Boletim de urna — 1º turno (MG) |
| `bweb_2t_MG_261020260742.csv` | Resultados 2026 — Boletim de urna — 2º turno (MG) |
| `eleitorado_local_votacao_2026_MG.csv` | Eleitorado 2026 — Eleitorado por local de votação |


Malha municipal: API de malhas do IBGE (`servicodados.ibge.gov.br/api/v3/malhas/municipios/3162500`).

