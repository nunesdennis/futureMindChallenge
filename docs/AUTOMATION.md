# Automação E2E FinGuard com Playwright

Guia de referência para a automação de testes end-to-end do FinGuard usando **Playwright com Python**.

---

## Contexto do Projeto de Automação

O FinGuard é uma aplicação Flask com server-side rendering (Jinja2) — sem SPA, sem roteamento client-side. Toda navegação gera requisições HTTP completas ao servidor. A classificação IA (Claude) é síncrona durante o POST de criação, o que torna esse endpoint o mais lento da aplicação.

**URL base de testes:** `https://poc.nunesdennis.me`

---

## Stack de Automação

- **Playwright** — automação e interação com browser
- **Pytest** — orquestração dos testes
- **Python 3.14** — runtime

### Instalação

```bash
pip install playwright pytest pytest-playwright
python -m playwright install chromium
```

---

## Estrutura de Diretórios

```
futureMindChallenge/
├── docs/
│   ├── AUTOMATION.md                    # Este arquivo
│   ├── TEST_PLAN.md                     # Plano detalhado de testes
│   └── ARCHITECTURE.md                  # Referência de seletores
├── tests/
│   ├── e2e/
│   │   ├── conftest.py                  # Fixtures do Pytest
│   │   ├── test_01_lista_reclamacoes.py
│   │   ├── test_02_criar_reclamacao.py
│   │   ├── test_03_detalhe_reclamacao.py
│   │   ├── test_04_atualizar_status.py
│   │   ├── test_05_apagar_reclamacao.py
│   │   ├── test_06_filtros_paginacao.py
│   │   └── test_07_dashboard.py
│   └── results/                         # Relatórios e screenshots
├── README.md
└── CLAUDE.md
```

---

## Suites de Testes

| Suite | Arquivo | Testes | Descrição |
|-------|---------|--------|-----------|
| **1** | `test_01_lista_reclamacoes.py` | 10 | Carregamento da página principal, tabela, navegação |
| **2** | `test_02_criar_reclamacao.py` | 14 | Formulário de nova reclamação, validação, submissão |
| **3** | `test_03_detalhe_reclamacao.py` | 14 | Detalhes da reclamação, classificação IA, urgência crítica |
| **4** | `test_04_atualizar_status.py` | 7 | Atualização de status da reclamação |
| **5** | `test_05_apagar_reclamacao.py` | 6 | Exclusão de reclamação com confirmação |
| **6** | `test_06_filtros_paginacao.py` | 15 | Filtros por canal/urgência/status, paginação |
| **7** | `test_07_dashboard.py` | 25 | KPIs, gráficos, tabela de dados, responsividade |

**Total:** 91 testes estruturados

---

## Status Atual (28 de Julho de 2026)

✅ **86 testes passando**  
❌ **5 testes falhando** (problemas menores de validação e encoding)

### Testes Falhando:

1. `test_02_contador_registros_visível` — Seletor não encontrado
2. `test_05_submissao_sem_canal_erro` — Validação de campo não implementada
3. `test_06_submissao_sem_texto_erro` — Validação de campo não implementada
4. `test_03_confirmar_exclui_registro` — Dados do BD podem estar duplicados
5. `test_06_filtro_status_analise` — Diferença em URL encoding

---

## Como Executar os Testes

### Todos os testes
```bash
cd tests/e2e && python -m pytest . -v
```

### Uma suite específica
```bash
pytest test_02_criar_reclamacao.py -v
```

### Um teste específico
```bash
pytest test_01_lista_reclamacoes.py::TestListaReclamacoes::test_01_titulo_carrega_correto -v
```

### Com relatório
```bash
pytest . -v --html=../results/report.html
```

### Com padrão de nome
```bash
pytest -k "lista" -v
```

---

## Dados de Teste

### Canais disponíveis
- SAC
- Ouvidoria
- Banco Central
- Redes Sociais
- Reclame Aqui

### Produtos disponíveis
- Cartão de Crédito
- Conta Corrente
- Empréstimo
- Investimentos
- Seguros

### Status disponíveis
- Aberta
- Em análise
- Resolvida

### Urgências disponíveis
- Baixa
- Média
- Alta
- Crítica

---

## Comportamentos Importantes

### Toggle de campo data
O campo `#campo_data` começa oculto. Aparece ao selecionar "Não" em "É a primeira ocorrência?":

```python
await page.click("input[name='primeira_ocorrencia'][value='nao']")
await page.wait_for_selector("div#campo_data", state="visible", timeout=30000)
await page.fill("input#data_reclamacao", "2024-06-15")
```

### Confirmação ao deletar
O botão "Deletar" dispara um `confirm()` nativo do browser:

```python
page.on("dialog", lambda dialog: dialog.accept())
await page.click("form[action*='/apagar'] button")
```

### Timeout na criação
O POST aguarda classificação síncrona do agente Claude (até 45s):

```python
await page.click("button[type='submit'].btn-primary")
await page.wait_for_selector("div.flash.sucesso", timeout=45000)
```

---

## Próximos Passos

1. **Corrigir testes falhando** — Validar seletores e encoding
2. **Adicionar testes de performance** — Medir tempos de resposta
3. **Integração CI/CD** — Executar testes automaticamente
4. **Relatórios visuais** — Screenshots e vídeos de falhas
