# Arquitetura de Seletores — FinGuard

Referência completa de seletores CSS/XPath por página da aplicação.

---

## Layout Global (`base.html`)

| Elemento | Seletor |
|----------|---------|
| Logo / título no header | `header h1` |
| Link "Reclamações" no nav | `nav a[href="/"]` |
| Botão "+ Nova Reclamação" no nav | `nav a[href="/nova"]` |
| Link "Dashboard" no nav | `nav a[href="/dashboard"]` |
| Flash de sucesso | `div.flash.sucesso` |
| Flash de erro | `div.flash.erro` |
| Footer | `footer` |

---

## Página de Lista (`/` — `index.html`)

| Elemento | Seletor |
|----------|---------|
| Título da página | `h2` (texto: "Reclamações Registradas") |
| Info de total/contagem | `p.total-info` |
| Filtro Canal (select) | `select[name="canal"]` |
| Filtro Urgência (select) | `select[name="urgencia"]` |
| Filtro Status (select) | `select[name="status"]` |
| Botão "Aplicar Filtros" | `button.btn-primary` (dentro de `form.filtros`) |
| Botão "Limpar Filtros" | `a.btn-secondary` (dentro de `form.filtros`) |
| Tabela de reclamações | `table` |
| Linhas da tabela (tbody) | `table tbody tr` |
| Coluna ID de uma linha | `table tbody tr:first-child td:nth-child(1)` |
| Badge de urgência | `span.badge[class*="badge-"]` |
| Badge de status | `span.badge[class*="badge-aberta"], span.badge[class*="badge-analise"], span.badge[class*="badge-resolvida"]` |
| Botão "Ver" (por linha) | `a.btn-secondary.btn-sm` (dentro de `td`) |
| Botão "Deletar" (por linha) | `form[action*="/apagar"] button` |
| Paginação | `div.paginacao` |
| Link "Próxima" | `div.paginacao a:last-child` |
| Página atual | `div.paginacao span.atual` |

---

## Formulário de Nova Reclamação (`/nova` — `nova.html`)

| Elemento | Seletor |
|----------|---------|
| Select Canal | `select#canal` ou `select[name="canal"]` |
| Select Produto | `select#produto` ou `select[name="produto"]` |
| Textarea do texto | `textarea#texto_reclamacao` ou `textarea[name="texto_reclamacao"]` |
| Radio "Sim" (primeira ocorrência) | `input[name="primeira_ocorrencia"][value="sim"]` |
| Radio "Não" (primeira ocorrência) | `input[name="primeira_ocorrencia"][value="nao"]` |
| Campo data (oculto/visível) | `div#campo_data` / `input#data_reclamacao` |
| Botão "Registrar e Classificar" | `button[type="submit"].btn-primary` |
| Botão "Cancelar" | `a.btn-secondary[href="/"]` |
| Aviso do agente IA | `div.aviso-ia` |

---

## Detalhe de Reclamação (`/reclamacao/<id>` — `detalhe.html`)

| Elemento | Seletor |
|----------|---------|
| Link "← Voltar" | `a.voltar` |
| ID da reclamação (h2) | `h2` (dentro do div de cabeçalho) |
| Data de registro | `span` com texto "Registrada em..." |
| Banner urgência crítica | `div.critica-box` |
| Card Dados da Reclamação | `div.card:first-child` (coluna esquerda) |
| Campo Canal | `div.campo-row:nth-child(1) span.valor` |
| Campo Produto | `div.campo-row:nth-child(2) span.valor` |
| Badge de Status | `div.campo-row span.badge` (card esquerdo) |
| Select atualizar status | `form.status-form select[name="status"]` |
| Botão "Atualizar status" | `form.status-form button[type="submit"]` |
| Texto original | `div.texto-box` |
| Card classificação agente | `div.card` (coluna direita) |
| Campo Categoria | `.campo-row:has(.label:contains("Categoria")) .valor` |
| Campo Urgência | `.campo-row:has(.label:contains("Urgência")) .badge` |
| Campo Sentimento | `.campo-row:has(.label:contains("Sentimento")) .badge` |
| Prazo de resposta | `.campo-row:has(.label:contains("Prazo")) .valor` |
| Responsável | `.campo-row:has(.label:contains("Responsável")) .valor` |
| Resumo LGPD | `div.resumo-box` |
| Ações imediatas | `div.acoes-box` |
| Sem classificação | `p` com texto "Reclamação ainda não classificada..." |

---

## Dashboard (`/dashboard` — `dashboard.html`)

| Elemento | Seletor |
|----------|---------|
| Heading principal | `h1` ou `h2` (texto: "Dashboard") |
| Badge "Live" | `span.badge-live` ou `.pulse` |
| KPI Cards | `div.kpi-card` ou `div.stat-card` |
| Valor do KPI | `div.kpi-value` ou `.stat-value` |
| Rótulo do KPI | `div.kpi-label` ou `.stat-label` |
| Gráficos | `canvas` |
| Tabela de dados | `table` |
| Headers da tabela | `thead tr` |
| Linhas da tabela | `tbody tr` |
| Badges de status | `span.badge[class*="badge-"]` |
| Container responsivo | `div.container` ou `div.grid` |
| Link "Nova Reclamação" | `a[href="/nova"]` |

---

## Padrões de Uso

### Selecionar opção em dropdown
```python
await page.select_option("select[name='canal']", "SAC")
await page.select_option("select[name='urgencia']", "Crítica")
```

### Preencher textarea
```python
await page.fill("textarea[name='texto_reclamacao']", "Texto da reclamação...")
```

### Clicar em botão
```python
await page.click("button[type='submit'].btn-primary")
```

### Aguardar elemento visível
```python
await page.wait_for_selector("div.flash.sucesso", state="visible", timeout=30000)
```

### Obter texto de elemento
```python
text = await page.text_content("div.campo-row span.valor")
```

### Contar elementos
```python
count = await page.locator("table tbody tr").count()
```

---

## Variáveis CSS Importantes

- **Cores principais:** `#0d3b6e` (azul escuro)
- **Cores de status:**
  - Aberta: `#FFC107` (amarelo)
  - Em análise: `#17A2B8` (ciano)
  - Resolvida: `#28A745` (verde)
- **Urgências:**
  - Baixa: `#28A745` (verde)
  - Média: `#FFC107` (amarelo)
  - Alta: `#FD7E14` (laranja)
  - Crítica: `#DC3545` (vermelho)
