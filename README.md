# FinGuard — Gestão de Reclamações Bancárias

Sistema web para registro, classificação automática e gestão de reclamações de clientes bancários, desenvolvido como projeto de treinamento de IA (Future Minds Challenge — Desafio 3).

---

## Visão Geral

O FinGuard permite que operadores de SAC registrem reclamações recebidas por diferentes canais. Ao submeter uma reclamação, um agente de IA (Claude) analisa o texto e aplica automaticamente as regras da política interna **POL-SAC-001 v2.0**, determinando:

- Categoria da reclamação
- Nível de urgência e prazo de resposta
- Sentimento do cliente
- Resumo padronizado (em conformidade com a LGPD)
- Ações imediatas recomendadas
- Área responsável pelo atendimento

**URL de produção/staging:** https://poc.nunesdennis.me

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3 + Flask 3.0 |
| Banco de dados | SQLite (via Flask-SQLAlchemy) |
| Templates | Jinja2 (server-side rendering) |
| Frontend | HTML + CSS + JavaScript vanilla |
| IA | Claude (Anthropic API) |
| Deploy | GitHub Actions + Cloudflare Tunnel + SSH (Debian) |

---

## Estrutura do Projeto

```
futureMindChallenge/
├── app.py                          # Aplicação Flask — rotas e lógica principal
├── models.py                       # Modelo SQLAlchemy (tabela dataset_finguard_desafio_3)
├── classifier.py                   # Agente Claude — classificação por POL-SAC-001
├── seed.py                         # Script para popular o BD com dados do CSV
├── reclassify.py                   # Reclassifica registros existentes (4 workers)
├── requirements.txt                # Dependências Python
├── .env.example                    # Template de variáveis de ambiente
├── templates/
│   ├── base.html                   # Layout base (header, nav, footer, flash messages)
│   ├── index.html                  # Lista de reclamações com filtros e paginação
│   ├── nova.html                   # Formulário de criação de reclamação
│   └── detalhe.html                # Detalhes da reclamação + atualização de status
└── requirements - documentation/
    ├── [BIT_BYTE] Future Minds 3 — O Desafio.pdf
    └── KS_POLITICA_INTERNA.pdf     # POL-SAC-001 v2.0
```

---

## Rotas da Aplicação

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Lista todas as reclamações com filtros e paginação (20/página) |
| GET | `/nova` | Formulário de nova reclamação |
| POST | `/nova` | Processa e cria a reclamação (dispara classificação IA) |
| GET | `/reclamacao/<id>` | Detalhes completos de uma reclamação |
| POST | `/reclamacao/<id>/status` | Atualiza o status da reclamação |
| POST | `/reclamacao/<id>/apagar` | Remove a reclamação do banco |

---

## Fluxo Principal

```
Operador acessa /nova
        │
        ▼
Preenche canal + texto (obrigatórios)
        │
        ▼
POST /nova → Flask gera ID: REC-{ano}-{#####}
        │
        ▼
Agente Claude analisa o texto (POL-SAC-001)
        │
        ├── Sucesso: salva classificação completa
        └── Falha API: aplica regras de fallback local
        │
        ▼
Redirect para /reclamacao/<ID> com flash de sucesso
```

---

## Campos do Modelo de Dados

| Campo | Tipo | Preenchido por |
|-------|------|----------------|
| `id` | String (REC-YYYY-#####) | Sistema (automático) |
| `data_reclamacao` | Date | Operador |
| `canal` | String | Operador |
| `produto` | String (nullable) | Operador / Agente |
| `texto_reclamacao` | Text | Operador |
| `status` | String (Aberta/Em análise/Resolvida) | Operador |
| `categoria` | String (nullable) | Agente IA |
| `sentimento` | String (nullable) | Agente IA |
| `urgencia` | String (nullable) | Agente IA |
| `resumo` | Text (nullable) | Agente IA |
| `acoes_imediatas` | Text (nullable) | Agente IA |
| `responsavel` | String (nullable) | Agente IA |
| `prazo_resposta` | String (nullable) | Agente IA |

---

## Regras de Negócio — Urgência (POL-SAC-001 v2.0)

| Nível | Prazo | Gatilhos |
|-------|-------|---------|
| Crítica | até 4h | Fraude, Banco Central, Procon, vulnerabilidade emocional, advogado |
| Alta | até 24h | Valor > R$500, múltiplas tentativas, ameaça de escalada |
| Média | até 3 dias | Recorrência, Ouvidoria, cobranças |
| Baixa | até 5 dias | Dúvidas, informações gerais |

---

## Configuração Local

### Pré-requisitos

- Python 3.10+
- Chave de API da Anthropic (`ANTHROPIC_API_KEY`)

### Instalação

```bash
# Clonar o repositório
git clone <repo-url>
cd futureMindChallenge

# Criar e ativar virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env e preencher ANTHROPIC_API_KEY

# Popular banco com dados de exemplo (opcional)
python seed.py

# Iniciar a aplicação
python app.py
```

A aplicação estará disponível em `http://localhost:5000`.

---

## Variáveis de Ambiente

| Variável | Obrigatória | Padrão | Descrição |
|----------|------------|--------|-----------|
| `ANTHROPIC_API_KEY` | Sim | — | Chave da API Claude (Anthropic) |
| `SECRET_KEY` | Não | `finguard-dev-secret` | Segredo Flask para sessões |
| `HOST` | Não | `0.0.0.0` | Host do servidor |
| `PORT` | Não | `5000` | Porta do servidor |
| `FLASK_DEBUG` | Não | `1` | Modo debug (0 para produção) |

---

## Deploy

O deploy é realizado automaticamente via GitHub Actions ao fazer push na branch `main`:

1. GitHub Actions é acionado
2. Instala o `cloudflared`
3. Conecta ao servidor via SSH com ProxyCommand Cloudflare
4. Executa `git pull` + reinstala dependências
5. Reinicia o serviço via `systemctl restart meu-python-app`

---

## Canais e Produtos Suportados

**Canais:** SAC, Ouvidoria, Banco Central, Redes Sociais, Reclame Aqui

**Produtos:** Cartão de Crédito, Conta Corrente, Empréstimo, Investimentos, Seguros
