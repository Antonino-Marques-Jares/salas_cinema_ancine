"""
ANCINE - Salas de Cinema (a partir de 2014)
Autor original: Antonino Marques Jares
Adaptado para script .py

Fonte: https://dados.ancine.gov.br/dados-abertos/salas-de-exibicao-evolucao-anual.json
"""

import os
import json
import warnings
from datetime import datetime

import numpy as np
import pandas as pd

# ------------------------------------------------------------------
# Configuração do FFmpeg ANTES de importar o bar_chart_race/matplotlib
# ------------------------------------------------------------------
import imageio_ffmpeg
import matplotlib
matplotlib.use("Agg")  # backend não interativo (necessário p/ vídeo)
import matplotlib.pyplot as plt

# Diz ao matplotlib para usar o FFmpeg embutido no imageio-ffmpeg
plt.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()

import bar_chart_race as bcr  # importar DEPOIS da config do ffmpeg

warnings.filterwarnings("ignore")

# ============================================================
# Configuração das pastas de saída
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
JSON_DIR = os.path.join(BASE_DIR, "json")
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


def carregar_dados(url: str) -> pd.DataFrame:
    """Baixa e normaliza os dados da ANCINE."""
    df = pd.read_json(url)
    df = pd.json_normalize(df["data"])

    # Adiciona coluna PAIS
    df["PAIS"] = "Brasil"

    # Reordena colunas
    nova_ordem = ["PAIS", "UF", "MUNICIPIO", "ANO", "STATUS", "REGISTRO_ANCINE"]
    df = df[nova_ordem]
    return df


def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia, traduz UF e converte STATUS para 0/1."""
    nome_estado = {
        "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
        "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
        "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
        "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
        "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco",
        "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
        "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
        "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
        "TO": "Tocantins",
    }

    df = df.rename(columns={"UF": "ESTADO", "REGISTRO_ANCINE": "ID"})
    df["ESTADO"] = df["ESTADO"].map(nome_estado)

    # STATUS -> 1 se ABERTA, 0 caso contrário
    df["STATUS"] = df["STATUS"].apply(lambda x: 1 if x == "ABERTA" else 0)
    return df


def obter_intervalo_anos(df: pd.DataFrame):
    """Retorna (ano_min, ano_max) a partir da coluna ANO."""
    ano_min = int(df["ANO"].min())
    ano_max = int(df["ANO"].max())
    return ano_min, ano_max


def gerar_pivot_estado(df_modelo: pd.DataFrame):
    """Agrupa por ESTADO/ANO e gera pivot para bar_chart_race."""
    df_estado = df_modelo[["ESTADO", "ANO", "STATUS", "ID"]].copy()
    df_estado = (
        df_estado.groupby(["ESTADO", "ANO"])["STATUS"].sum().reset_index()
    )
    df_estado = df_estado.rename(columns={"STATUS": "TOTAL", "ANO": "DATA"})
    df_estado = df_estado.sort_values("DATA")
    df_estado["DATA"] = pd.to_datetime(
        df_estado["DATA"].astype(str), format="%Y"
    )
    df_pivot = (
        df_estado.pivot(index="DATA", columns="ESTADO", values="TOTAL").fillna(0)
    )
    return df_pivot, df_estado


def gerar_pivot_regiao(df_estado: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por REGIAO e gera pivot para bar_chart_race."""
    mapeamento_regioes = {
        # Norte
        "Amazonas": "NORTE", "Roraima": "NORTE", "Amapá": "NORTE",
        "Pará": "NORTE", "Tocantins": "NORTE", "Rondônia": "NORTE",
        "Acre": "NORTE",
        # Nordeste
        "Maranhão": "NORDESTE", "Piauí": "NORDESTE", "Ceará": "NORDESTE",
        "Rio Grande do Norte": "NORDESTE", "Pernambuco": "NORDESTE",
        "Paraíba": "NORDESTE", "Sergipe": "NORDESTE", "Alagoas": "NORDESTE",
        "Bahia": "NORDESTE",
        # Centro-Oeste
        "Mato Grosso": "CENTRO-OESTE", "Mato Grosso do Sul": "CENTRO-OESTE",
        "Goiás": "CENTRO-OESTE", "Distrito Federal": "CENTRO-OESTE",
        # Sudeste
        "São Paulo": "SUDESTE", "Rio de Janeiro": "SUDESTE",
        "Espírito Santo": "SUDESTE", "Minas Gerais": "SUDESTE",
        # Sul
        "Paraná": "SUL", "Rio Grande do Sul": "SUL", "Santa Catarina": "SUL",
    }

    df_regiao = df_estado.copy()
    df_regiao["REGIAO"] = df_regiao["ESTADO"].map(mapeamento_regioes)
    df_regiao = df_regiao[["REGIAO", "DATA", "TOTAL"]]
    df_regiao = df_regiao.sort_values("DATA")
    df_regiao = (
        df_regiao.groupby(["REGIAO", "DATA"])["TOTAL"].sum().reset_index()
    )
    df_pivot = (
        df_regiao.pivot(index="DATA", columns="REGIAO", values="TOTAL").fillna(0)
    )
    return df_pivot


def gerar_json_ancine() -> str:
    """
    Gera o arquivo json/ancine.json contendo APENAS os metadados.
    O campo 'dados' fica vazio ([]).
    Retorna o caminho do arquivo criado.
    """
    caminho_json = os.path.join(JSON_DIR, "ancine.json")

    # Data atual no formato ISO (YYYY-MM-DD)
    data_atual = datetime.now().strftime("%Y-%m-%d")

    conteudo = {
        "metadados": {
            "data_de_atualizacao": data_atual,
            "responsavel": "Antonino Marques Jares",
            "nome_programa": "etl_atualizar_ancine_no_site.py",
        },
        "dados": [],
    }

    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)

    print(f"JSON gerado -> {caminho_json}")
    return caminho_json


def main():
    url = "https://dados.ancine.gov.br/dados-abertos/salas-de-exibicao-evolucao-anual.json"

    print("Baixando e tratando dados da ANCINE...")
    df = carregar_dados(url)
    df_modelo = tratar_dados(df)

    # ---------- Gera o JSON apenas com metadados ----------
    gerar_json_ancine()

    # ---------- Intervalo de anos dinâmico ----------
    ano_min, ano_max = obter_intervalo_anos(df_modelo)
    intervalo = f"{ano_min}-{ano_max}"
    print(f"Intervalo de anos encontrado no JSON: {intervalo}")

    # ---------- Por Estado ----------
    df_pivot_estado, df_estado = gerar_pivot_estado(df_modelo)

    caminho_estado = os.path.join(VIDEOS_DIR, "salas_cinema_por_estado_brasil.mp4")
    print(f"Gerando vídeo por estado -> {caminho_estado}")
    bcr.bar_chart_race(
        df=df_pivot_estado,
        filename=caminho_estado,
        orientation="h",
        title=f"Salas de cinema da ANCINE ativas por Estado ({intervalo})",
        title_size=14,
        bar_label_size=8,
        tick_label_size=7,
    )

    # ---------- Por Região ----------
    df_pivot_regiao = gerar_pivot_regiao(df_estado)

    caminho_regiao = os.path.join(VIDEOS_DIR, "salas_cinema_por_regiao_brasil.mp4")
    print(f"Gerando vídeo por região -> {caminho_regiao}")
    bcr.bar_chart_race(
        df=df_pivot_regiao,
        filename=caminho_regiao,
        orientation="h",
        title=f"Salas de cinema da ANCINE ativas por Região ({intervalo})",
        title_size=14,
        bar_label_size=8,
        tick_label_size=7,
    )

    print("\nConcluído! Vídeos salvos em:", VIDEOS_DIR)
    print("JSON salvo em:", JSON_DIR)


if __name__ == "__main__":
    main()
