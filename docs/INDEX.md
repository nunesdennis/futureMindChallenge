# Documentação — FinGuard

Índice completo de documentação do projeto de automação E2E.

---

## 📑 Documentação de Automação

### 🚀 [AUTOMATION.md](./AUTOMATION.md)
Guia geral de automação end-to-end com Playwright.

**Conteúdo:**
- Stack e instalação
- Estrutura de diretórios
- Suites de testes (resumo)
- Como executar testes
- Dados de teste
- Comportamentos importantes
- Próximos passos

**Para:** Desenvolvedor novo no projeto que quer entender a estratégia geral.

---

### 📋 [TEST_PLAN.md](./TEST_PLAN.md)
Plano detalhado de testes com cobertura completa.

**Conteúdo:**
- Resumo executivo (86/91 testes passando)
- Cada suite explicada em detalhes
- Cada teste listado com status e descrição
- Prioridade de testes
- Próximos passos

**Para:** QA/Engenheiro de testes que precisa gerenciar e expandir testes.

---

### 🏗️ [ARCHITECTURE.md](./ARCHITECTURE.md)
Referência de seletores CSS por página.

**Conteúdo:**
- Layout global
- Página de lista
- Formulário de criação
- Página de detalhe
- Dashboard
- Padrões de uso com Playwright
- Variáveis CSS importantes

**Para:** Engenheiro que está escrevendo ou debugando testes.

---

## 📂 Estrutura do Projeto

```
futureMindChallenge/
│
├── docs/                            ← Documentação (você está aqui)
│   ├── INDEX.md                     ← Este arquivo
│   ├── AUTOMATION.md                ← Guia geral
│   ├── TEST_PLAN.md                 ← Plano detalhado
│   └── ARCHITECTURE.md              ← Seletores CSS
│
├── tests/                           ← Testes E2E
│   ├── README.md                    ← Como rodar testes
│   ├── e2e/                         ← Suite de testes
│   │   ├── conftest.py              ← Configuração Pytest
│   │   ├── test_01_lista_reclamacoes.py    (10 testes)
│   │   ├── test_02_criar_reclamacao.py     (14 testes)
│   │   ├── test_03_detalhe_reclamacao.py   (14 testes)
│   │   ├── test_04_atualizar_status.py     (7 testes)
│   │   ├── test_05_apagar_reclamacao.py    (6 testes)
│   │   ├── test_06_filtros_paginacao.py    (15 testes)
│   │   └── test_07_dashboard.py            (25 testes)
│   └── results/                     ← Relatórios e screenshots
│
├── app.py                           ← Aplicação Flask
├── classifier.py                    ← Agente Claude para classificação
├── models.py                        ← Modelos de dados
├── seed.py                          ← Script de seed de dados
├── requirements.txt                 ← Dependências Python
├── README.md                        ← Documentação principal do projeto
└── .env.example                     ← Variáveis de ambiente
```

---

## 🎯 Quick Start

### 1️⃣ Ler Documentação
```
AUTOMATION.md (5 min)
  ↓
TEST_PLAN.md (10 min)
  ↓
ARCHITECTURE.md (5 min)
```

### 2️⃣ Executar Testes
```bash
cd tests/e2e
python -m pytest . -v
```

### 3️⃣ Debugar Falha
Procure o teste em `TEST_PLAN.md` → Veja seletor em `ARCHITECTURE.md` → Corrija em `test_XX_*.py`

---

## 📊 Status do Projeto

**Data:** 28 de Julho de 2026

**Testes:** 86 ✅ / 91 (5 falhando)

**Tempo:** ~10 minutos para executar

**Suites Prontas:** 7/7

**Dashboard:** ✅ Completamente funcional (25/25 testes)

---

## 🔍 Navegação por Papel

### Desenvolvedor Frontend
1. Leia `AUTOMATION.md` (stack geral)
2. Consulte `ARCHITECTURE.md` (seletores CSS)
3. Use `tests/README.md` (como rodar localmente)

### QA/Tester
1. Estude `TEST_PLAN.md` (cobertura)
2. Entenda `AUTOMATION.md` (estratégia)
3. Use `tests/README.md` (execução)

### DevOps/CI-CD
1. Consulte `tests/README.md` (comandos)
2. Use `TEST_PLAN.md` (interpretação de resultados)

### Gerente de Projeto
1. Revise `TEST_PLAN.md` (overview)
2. Acompanhe status em `STATUS_CURRENT` (abaixo)

---

## 📈 Status Atual Resumido

| Aspecto | Status |
|---------|--------|
| **Automação E2E** | ✅ Completa |
| **Cobertura** | 91 testes em 7 suites |
| **Taxa de Sucesso** | 94.5% (86/91) |
| **Dashboard** | ✅ Totalmente funcional |
| **Fluxo Principal** | ✅ 100% funcional |
| **Filtros** | ✅ 93% funcional (14/15) |
| **CI/CD** | 🔄 Pronto para integração |

---

## 🚀 Próximas Ações

### Curto Prazo (Esta Semana)
- [ ] Corrigir 5 testes falhando
- [ ] Validar seletores CSS
- [ ] Verificar encoding de URLs

### Médio Prazo (Próximo Mês)
- [ ] Integração com GitHub Actions
- [ ] Relatórios automáticos
- [ ] Testes de performance

### Longo Prazo (Roadmap)
- [ ] Testes de carga
- [ ] Testes de acessibilidade (WCAG)
- [ ] Cobertura móvel avançada

---

## 🔗 Links Úteis

- **URL da App:** https://poc.nunesdennis.me
- **GitHub:** [repositório do projeto]
- **CI/CD:** [workflow de testes]

---

## 📞 Suporte

Para dúvidas sobre testes:
1. Consulte a documentação acima
2. Procure no `TEST_PLAN.md`
3. Valide seletores em `ARCHITECTURE.md`
4. Leia comentários em `test_XX_*.py`

---

**Última atualização:** 28 de Julho de 2026
