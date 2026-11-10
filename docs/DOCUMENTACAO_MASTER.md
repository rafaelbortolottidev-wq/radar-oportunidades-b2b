# P05 — Radar de Oportunidades B2B

**Documento:** Documentação técnica master  
**Atualização:** 10/11/2026  
**Status:** Camada Bronze implementada e validada; Silver e Gold pendentes.

## 1. Visão geral

Projeto de Engenharia de Dados para construir uma base analítica de oportunidades comerciais a partir de dados públicos do CNPJ. O foco principal é a experiência prática com Databricks, PySpark, Delta Lake, Unity Catalog e práticas de engenharia de dados aplicáveis ao mercado.

**Recorte de negócio planejado:** restaurantes ativos em Campinas/SP, CNAE principal `5611201`, situação cadastral `02` e código de município da Receita Federal `6291`. Esse filtro ainda não foi implementado na camada Silver.

## 2. Escopo e arquitetura

**Abordagem:** processamento batch, ELT e arquitetura Lakehouse/Medallion.

```text
Receita Federal — Dados Abertos CNPJ (ZIP)
             |
             v
Extração local com Python (CSV)
             |
             v
Unity Catalog Volume — Raw
             |
             v
Bronze — tabela Delta Lake [IMPLEMENTADO]
             |
             v
Silver — padronização, qualidade e filtros [PENDENTE]
             |
             v
Gold — base analítica de oportunidades [PENDENTE]
```

- **Raw:** arquivo CSV de origem armazenado em Volume; não é uma tabela Delta.
- **Bronze:** tabela Delta com campos de origem preservados como `string`, sem transformações de negócio.
- **Silver:** etapa futura de nomeação das colunas, tipagem, qualidade, deduplicação e aplicação de filtros.
- **Gold:** etapa futura de modelagem das oportunidades comerciais.

## 3. Ferramentas e ambiente

| Componente | Uso no P05 |
|---|---|
| Windows, VS Code e Python | Preparação/extração local de arquivos e documentação |
| Databricks Free Edition | Execução dos notebooks |
| PySpark | Leitura e persistência dos dados |
| Unity Catalog | Organização do Volume e da tabela |
| Delta Lake | Formato de armazenamento da Bronze |
| Git/GitHub | Versionamento pelo GitHub Flow |

**Não implementados até esta data:** integração AWS do P05, automação recorrente da ingestão, Lakeflow Jobs, CI/CD, Silver, Gold, MERGE e histórico de snapshots.

## 4. Dados de origem

- **Fonte:** Receita Federal — Dados Abertos do CNPJ.
- **Arquivo ZIP trabalhado:** `Estabelecimentos9.zip`.
- **CSV extraído:** `Estabelecimentos9.csv`.
- **Formato:** CSV sem cabeçalho; separador `;`; codificação Latin-1; 30 campos.
- **Tamanho observado do CSV:** aproximadamente 1,06 GB.
- **Cobertura:** um arquivo de estabelecimentos, **não** a base completa de todos os CNPJs brasileiros.

Foram considerados também arquivos de municípios para associação dos códigos da Receita Federal com nomes de municípios; a preparação definitiva dessa associação ainda está pendente no pipeline Databricks.

## 5. Extração e área Raw

**Script local:** `scripts/01_extrair_csv_estabelecimentos.py` (nome adotado para o projeto; verificar sua localização antes do commit).

A extração/preparação foi feita localmente e o CSV foi enviado manualmente ao Databricks. O arquivo de origem está em um Volume denominado `radar_b2b_raw`, no contexto `workspace.default`.

**Limitação atual:** não existe carga automatizada nem controle de versionamento de arquivos da Receita Federal. Arquivos de dados brutos não devem ser enviados ao GitHub.

## 6. Bronze — implementação validada

**Notebook:** `01_bronze_estabelecimentos`  
**Tabela Delta:** `workspace.bronze.estabelecimentos`

### Célula 1 — Leitura do CSV

- Leitura utilizando PySpark.
- Campos `_c0` a `_c29`, todos como `string`.
- Inspeção com `printSchema()` e visualização dos primeiros cinco registros.
- Quantidade de colunas conferida usando `len(df_bronze.columns)`.

### Célula 2 — Criar schema Bronze

```python
# O QUE: Criar o schema Bronze no Unity Catalog.
# POR QUÊ: Organizar as tabelas de ingestão.
spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.bronze")
```

O comando cria o espaço lógico para tabelas; **não** carrega dados.

### Célula 3 — Gravar tabela Delta

```python
# O QUE: Gravar a tabela Bronze se ainda não existir.
# POR QUÊ: Evitar recriar ou duplicar a carga ao repetir o notebook.
tabela = "workspace.bronze.estabelecimentos"

if not spark.catalog.tableExists(tabela):
    df_bronze.write \
        .format("delta") \
        .mode("append") \
        .saveAsTable(tabela)
    print("Tabela Bronze criada com sucesso!")
else:
    print("A tabela já existe. Nenhuma carga realizada.")
```

**Decisão técnica:** o modo `errorifexists` apresentou erro de operação não suportada no ambiente utilizado. Foi substituído pela verificação `tableExists` antes da gravação. O uso de `append` nesse fluxo ocorre somente quando a tabela não existe. Isso evita duplicações em uma reexecução simples, mas **não constitui ingestão incremental** e não é proteção transacional contra execuções concorrentes.

### Célula 4 — Validação

```python
# O QUE: Conferir estrutura e volume da tabela persistida.
# POR QUÊ: Validar a Bronze antes de iniciar a Silver.
df_validacao = spark.table("workspace.bronze.estabelecimentos")
print(f"Colunas: {len(df_validacao.columns)}")
print(f"Registros: {df_validacao.count():,}")
```

**Resultado informado e validado na execução:**

| Indicador | Resultado |
|---|---:|
| Colunas | 30 |
| Registros | 4.753.435 |
| Formato | Delta Lake |
| Tabela | `workspace.bronze.estabelecimentos` |

A gravação e a leitura posterior da tabela foram concluídas. **Ainda falta** uma reconciliação formal entre total de linhas do CSV de origem e total persistido, além de verificações de completude e qualidade.

## 7. Decisões e padrões do projeto

1. Manter o arquivo original em **Raw** e a tabela persistida em **Bronze**.
2. Adiar regras de negócio e transformação de tipos para a **Silver**.
3. Registrar nos notebooks comentários curtos de **O QUE** e **POR QUÊ**.
4. Preferir código PySpark simples, legível, verificável e idempotente quando possível.
5. Usar GitHub Flow: `main` estável; branch por tarefa; testes; commit; push; Pull Request para `main`.
6. Não adicionar serviços AWS, mensageria ou automação sem necessidade concreta.
7. Minimizar consumo do ambiente gratuito; evitar reprocessamentos e leituras completas desnecessárias.

## 8. Repositório e documentação

**Repositório:** `radar-oportunidades-b2b`  
**Branch de trabalho mencionada:** `feature/estrutura-inicial` (confirmar a branch ativa antes de commitar).

Organização planejada:

```text
radar-oportunidades-b2b/
├── README.md
├── .gitignore
├── scripts/
│   └── 01_extrair_csv_estabelecimentos.py
├── notebooks/
│   └── 01_bronze_estabelecimentos
└── docs/
    └── DOCUMENTACAO_MASTER.md
```

**Atenção:** a sincronização/publicação do notebook Databricks no repositório ainda precisava ser confirmada. A estrutura acima é a estrutura-alvo, não a confirmação de que todos os arquivos já estão no GitHub.

O `README.md` apresenta a visão geral do projeto. Este documento mantém a descrição técnica, o histórico das decisões, os resultados validados e as pendências.

## 9. Próximas entregas

### Entrega 1 — Versionar a Bronze e a documentação

- Salvar `README.md` na raiz.
- Salvar este arquivo em `docs/DOCUMENTACAO_MASTER.md`.
- Confirmar a branch e o `git status`.
- Sincronizar o notebook Bronze do Databricks, conferindo seu conteúdo e sua localização.
- Fazer commit/push em branch de trabalho e abrir Pull Request para `main`.

### Entrega 2 — Silver

- Mapear as 30 colunas de estabelecimentos de acordo com o leiaute oficial da Receita Federal.
- Definir schema e conversões de tipos necessárias.
- Aplicar verificações de qualidade e chave de estabelecimento.
- Implementar o recorte de restaurantes ativos de Campinas/SP.
- Validar contagens, duplicidades e consistência.

### Entrega 3 — Gold

- Modelar uma tabela analítica de estabelecimentos elegíveis para prospecção.
- Definir indicadores e critérios de oportunidade.
- Validar consultas SQL e resultados.

### Evolução posterior

- Cargas incrementais e snapshots com Delta Lake/MERGE, caso a frequência e a fonte justifiquem.
- Orquestração com Lakeflow Jobs.
- Testes automatizados, logs e monitoramento.
- CI/CD e governança no Unity Catalog.
- Integração AWS quando necessária, após avaliação de segurança e custos.

## 10. Custos, segurança e limitações

- O desenvolvimento atual utiliza a **Databricks Free Edition**, sujeito às limitações da oferta.
- Não presumir que serviços pagos da Databricks ou AWS estejam cobertos pela edição gratuita.
- Evitar processamento completo repetido do CSV de aproximadamente 1,06 GB sem necessidade.
- Não versionar grandes arquivos CSV/ZIP, credenciais, tokens ou segredos no GitHub.
- Dados públicos de CNPJ exigem avaliação de licença, procedência, finalidade e eventuais obrigações legais antes de disponibilização comercial.
- O P05 **não possui ainda** pipeline automatizado de ponta a ponta ou produto analítico final.

## 11. Checkpoint de continuidade

**Concluído:** arquivo da Receita Federal extraído e enviado ao Volume; leitura com PySpark; schema Bronze; tabela Delta; validação de **30 colunas e 4.753.435 registros**.

**Etapa imediata:** publicar e versionar README, documentação Master e notebook Bronze, após confirmar a branch e os arquivos efetivamente presentes no repositório.

**Próxima etapa de dados:** iniciar a Silver, começando pelo mapeamento das 30 colunas oficiais dos estabelecimentos.
