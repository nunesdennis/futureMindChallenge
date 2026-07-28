# Testes E2E — FinGuard

Testes automatizados end-to-end para validação da aplicação FinGuard com Playwright e Pytest.

---

## 📁 Estrutura

```
tests/
├── e2e/
│   ├── conftest.py                  # Configuração do Pytest e fixtures
│   ├── test_01_lista_reclamacoes.py (10 testes)
│   ├── test_02_criar_reclamacao.py  (14 testes)
│   ├── test_03_detalhe_reclamacao.py (14 testes)
│   ├── test_04_atualizar_status.py  (7 testes)
│   ├── test_05_apagar_reclamacao.py (6 testes)
│   ├── test_06_filtros_paginacao.py (15 testes)
│   └── test_07_dashboard.py         (25 testes)
├── results/                         # Relatórios e screenshots
└── README.md                        # Este arquivo
```

---

## 🚀 Como Executar

### Todos os testes
```bash
cd tests/e2e
python -m pytest . -v
```

### Uma suite específica
```bash
pytest test_02_criar_reclamacao.py -v
```

### Um teste específico
```bash
pytest test_01_lista_reclamacoes.py::TestListaReclamacoes::test_01_titulo_carrega_correto -v
```

### Com relatório HTML
```bash
pytest . -v --html=../results/report.html --self-contained-html
```

### Com padrão de nome
```bash
pytest -k "lista" -v
```

### Modo verbose com output
```bash
pytest . -vv -s
```

---

## 📊 Status Atual

✅ **86 testes passando**  
❌ **5 testes com falhas menores**

**Tempo de execução:** ~10 minutos

---

## 📚 Documentação

Veja em `docs/`:

- **[AUTOMATION.md](../docs/AUTOMATION.md)** — Guia geral de automação
- **[TEST_PLAN.md](../docs/TEST_PLAN.md)** — Plano detalhado de testes
- **[ARCHITECTURE.md](../docs/ARCHITECTURE.md)** — Referência de seletores CSS

---

## 🔧 Configuração

Edite `conftest.py` para:

- Alterar URL base (`BASE_URL`)
- Configurar timeouts
- Adicionar fixtures customizadas

---

## 🐛 Troubleshooting

### "Chromium not found"
```bash
python -m playwright install chromium
```

### "Timeout ao aguardar elemento"
Aumente o timeout em `conftest.py`:
```python
page.wait_for_timeout(60000)  # 60 segundos
```

### "Erro de encoding em URLs"
Use `urllib.parse.quote()` para encapsular caracteres especiais.

---

## 📝 Convenções

- **Nomes de teste:** `test_<numero>_<descricao>`
- **Classes:** `Test<SuiteNome>`
- **Fixtures:** Definidas em `conftest.py`
- **Assertions:** Use `assert` direto (Pytest)

---

## ✅ Checklist de Execução

- [ ] Abrir terminal em `tests/e2e`
- [ ] Executar `python -m pytest . -v`
- [ ] Verificar se Chrome abre
- [ ] Aguardar conclusão dos testes
- [ ] Revisar resultado final
- [ ] Gerar relatório se necessário

