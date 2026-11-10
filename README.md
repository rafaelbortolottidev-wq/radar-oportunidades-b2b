# Radar de Oportunidades B2B

Projeto de Engenharia de Dados para identificar oportunidades comerciais a partir de dados públicos de empresas brasileiras, utilizando Databricks, PySpark, Delta Lake e arquitetura Lakehouse.

## Objetivo

Construir um pipeline de dados para processar informações públicas da Receita Federal e disponibilizar uma base analítica para prospecção B2B.

O recorte inicial será estabelecimentos ativos em Campinas (SP).

## Arquitetura

**Abordagem:** ELT + processamento Batch.

```text
Receita Federal (CSV/ZIP)
         |
         v
Python — Extração do CSV
         |
         v
Unity Catalog Volume (Raw)
         |
         v
Bronze — Delta Lake
         |
         v
Silver — Tratamento e qualidade
         |
         v
Gold — Oportunidades B2B
```

As camadas Silver e Gold ainda serão implementadas.

## Tecnologias

- Python e PySpark
- Databricks Free Edition
- Delta Lake
- Unity Catalog
- Databricks SQL
- Git e GitHub

## Status do projeto

| Etapa | Status |
|---|---|
| Repositório e ambiente | Iniciado |
| Extração dos dados da Receita | Concluído |
| Upload para Unity Catalog Volume | Concluído |
| Bronze — Estabelecimentos | Concluído |
| Silver — Tratamento e qualidade | Pendente |
| Gold — Modelagem analítica | Pendente |
| MERGE e histórico de snapshots | Pendente |
| Orquestração e CI/CD | Pendente |

## Resultados validados

**Tabela:** `workspace.bronze.estabelecimentos`

- **4.753.435 registros**
- **30 colunas**
- Formato Delta Lake
- Fonte: `Estabelecimentos9.zip`

A tabela contém somente uma parte da base de estabelecimentos da Receita Federal, e não todos os CNPJs brasileiros.

## Organização do repositório

```text
radar-oportunidades-b2b/
├── scripts/
│   └── 01_extrair_csv_estabelecimentos.py
├── notebooks/
│   └── 01_bronze_estabelecimentos
├── docs/
│   └── DOCUMENTACAO_MASTER.md
├── .gitignore
└── README.md
```

Estrutura planejada para o repositório após a sincronização do notebook Databricks e a publicação da documentação.

Os arquivos brutos são armazenados separadamente e não serão versionados no GitHub.

## Próximas etapas

1. Concluir o versionamento da Bronze no GitHub.
2. Implementar a Silver com mapeamento e qualidade.
3. Implementar comparação de snapshots, MERGE e histórico.
4. Construir a Gold para segmentação de oportunidades comerciais.
5. Desenvolver orquestração, testes, monitoramento e CI/CD.

## Documentação técnica

Os detalhes de implementação e as decisões arquiteturais serão mantidos em `docs/DOCUMENTACAO_MASTER.md`.
