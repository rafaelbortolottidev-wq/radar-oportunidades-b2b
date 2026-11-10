"""
O QUE:
Extrai o arquivo CSV completo de estabelecimentos da Receita Federal, preservando os dados originais.

POR QUÊ:
Preparar os dados para ingestão na camada Bronze do Databricks, separando ingestão e transformação.
"""

from pathlib import Path
from zipfile import ZipFile
import shutil

# Localizar os arquivos de origem e destino.
pasta_projeto = Path(__file__).resolve().parents[1]
pasta_dados = pasta_projeto.parent / "dados_brutos"

arquivo_zip = pasta_dados / "Estabelecimentos9.zip"
arquivo_csv = pasta_dados / "estabelecimentos9.csv"

# Extrair o CSV completo, sem carregar os dados na memória.
with ZipFile(arquivo_zip) as zip_ref:
    arquivos = [nome for nome in zip_ref.namelist()
                if not nome.endswith("/")]

    if len(arquivos) != 1:
        raise ValueError("Esperado um único arquivo dentro do ZIP.")

    with zip_ref.open(arquivos[0]) as origem:
        with open(arquivo_csv, "wb") as destino:
            shutil.copyfileobj(origem, destino)

print(f"Arquivo preparado: {arquivo_csv.name}")
print(f"Tamanho: {arquivo_csv.stat().st_size:,} bytes")
