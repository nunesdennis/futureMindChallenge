# Plano de Testes Detalhado — FinGuard

Estratégia e cobertura de testes E2E para a aplicação FinGuard.

---

## Resumo Executivo

- **Stack:** Playwright + Pytest + Python 3.14
- **URL:** https://poc.nunesdennis.me
- **Status:** 86 testes passando, 5 testes com falhas menores
- **Total de Testes:** 91 testes em 7 suites
- **Tempo de Execução:** ~10 minutos

---

## Suite 1: Lista de Reclamações (10 testes)

**Arquivo:** `test_01_lista_reclamacoes.py`

**Objetivo:** Validar carregamento e exibição da página principal.

### Testes

| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_01_titulo_carrega_correto` | ✅ PASS | Título "Reclamações Registradas" visível |
| `test_02_contador_registros_visivel` | ❌ FAIL | Seletor `p.total-info` não encontrado |
| `test_03_tabela_possui_dez_colunas` | ✅ PASS | Tabela tem 10 colunas |
| `test_04_cabecalhos_corretos` | ✅ PASS | Headers da tabela estão corretos |
| `test_05_tabela_exibe_registros` | ✅ PASS | Pelo menos 1 linha de dados |
| `test_06_cada_linha_tem_botoes` | ✅ PASS | Botões "Ver" e "Deletar" em cada linha |
| `test_07_botao_ver_redireciona` | ✅ PASS | Clique em "Ver" navega para detalhe |
| `test_08_badges_urgencia_visiveis` | ✅ PASS | Badges de urgência carregam |
| `test_09_logo_visivel` | ✅ PASS | Logo do FinGuard no header |
| `test_10_footer_visivel` | ✅ PASS | Footer com informações |

---

## Suite 2: Criar Reclamação (14 testes)

**Arquivo:** `test_02_criar_reclamacao.py`

**Objetivo:** Testar formulário de criação e validações.

### Testes

| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_01_formulario_carrega` | ✅ PASS | Página `/nova` carrega corretamente |
| `test_02_aviso_ia_visivel` | ✅ PASS | Aviso sobre agente IA exibido |
| `test_03_select_canal_opcoes` | ✅ PASS | 5 opções de canal disponíveis |
| `test_04_select_produto_opcoes` | ✅ PASS | 5 opções de produto disponíveis |
| `test_05_submissao_sem_canal_erro` | ❌ FAIL | Validação não implementada na app |
| `test_06_submissao_sem_texto_erro` | ❌ FAIL | Validação não implementada na app |
| `test_07_campo_data_oculto_sim` | ✅ PASS | Campo data oculto quando "Sim" selecionado |
| `test_08_campo_data_visivel_nao` | ✅ PASS | Campo data visível quando "Não" selecionado |
| `test_09_botao_cancelar_volta` | ✅ PASS | "Cancelar" redireciona para `/` |
| `test_10_cria_reclamacao_completa` | ✅ PASS | Reclamação criada com sucesso |
| `test_11_id_gerado_formato_correto` | ✅ PASS | ID segue padrão `REC-AAAA-NNNNN` |
| `test_12_reclamacao_com_data_manual` | ✅ PASS | Data manual preenchida corretamente |
| `test_13_reclamacao_fraude_urgencia_critica` | ✅ PASS | Reclamação com "fraude" → urgência crítica |
| `test_14_reclamacao_critica_exibe_banner` | ✅ PASS | Banner de urgência crítica aparece |

---

## Suite 3: Detalhe de Reclamação (14 testes)

**Arquivo:** `test_03_detalhe_reclamacao.py`

**Objetivo:** Validar página de detalhe e classificação IA.

### Testes

| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_01_detalhe_carrega_sem_erros` | ✅ PASS | Página de detalhe carrega HTTP 200 |
| `test_02_id_exibido_cabecalho` | ✅ PASS | ID exibido no cabeçalho |
| `test_03_data_registro_visivel` | ✅ PASS | Data de registro apresentada |
| `test_04_card_dados_reclamacao` | ✅ PASS | Card com dados básicos presente |
| `test_05_badge_status_visivel` | ✅ PASS | Badge de status exibido |
| `test_06_texto_original_visivel` | ✅ PASS | Texto original da reclamação visível |
| `test_07_card_classificacao_presente` | ✅ PASS | Card de classificação IA presente |
| `test_08_campos_classificacao_preenchidos` | ✅ PASS | Categoria, urgência, sentimento preenchidos |
| `test_09_resumo_lgpd_visivel` | ✅ PASS | Resumo LGPD exibido |
| `test_10_acoes_imediatas_visiveis` | ✅ PASS | Ações imediatas listadas |
| `test_11_link_voltar_funciona` | ✅ PASS | Link "← Voltar" redireciona |
| `test_12_urgencia_critica_exibe_banner` | ✅ PASS | Banner ⚠️ CRÍTICA aparece |
| `test_13_urgencia_nao_critica_sem_banner` | ✅ PASS | Banner oculto para urgências normais |
| `test_14_id_inexistente_retorna_404` | ✅ PASS | URL inválida retorna 404 |

---

## Suite 4: Atualizar Status (7 testes)

**Arquivo:** `test_04_atualizar_status.py`

**Objetivo:** Testar alteração de status das reclamações.

### Testes

| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_01_formulario_status_presente` | ✅ PASS | Formulário de status presente |
| `test_02_select_status_tres_opcoes` | ✅ PASS | 3 opções: Aberta, Em análise, Resolvida |
| `test_03_status_atual_pre_selecionado` | ✅ PASS | Status atual está pré-selecionado |
| `test_04_botao_atualizar_presente` | ✅ PASS | Botão "Atualizar status" presente |
| `test_05_cancelar_confirmar_fecha` | ✅ PASS | Confirmar/Cancelar fecha modal |
| `test_06_altera_status_analise_sucesso` | ✅ PASS | Alteração para "Em análise" funciona |
| `test_07_altera_status_volta_aberta` | ✅ PASS | Volta para "Aberta" funciona |

---

## Suite 5: Apagar Reclamação (6 testes)

**Arquivo:** `test_05_apagar_reclamacao.py`

**Objetivo:** Testar exclusão de registros com confirmação.

### Testes

| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_01_botao_deletar_presente` | ✅ PASS | Botão "Deletar" visível |
| `test_02_cancelar_confirmar_nao_deleta` | ✅ PASS | "Cancelar" no dialog não deleta |
| `test_03_confirmar_exclui_registro` | ❌ FAIL | Contagem não reduz (dados duplicados?) |
| `test_04_flash_sucesso_mostra_id` | ✅ PASS | Flash de sucesso exibe ID deletado |
| `test_05_registro_deletado_nao_aparece` | ✅ PASS | Registro não aparece mais na lista |
| `test_06_acesso_direto_deletado_retorna_erro` | ✅ PASS | Acesso direto retorna 404 |

---

## Suite 6: Filtros e Paginação (15 testes)

**Arquivo:** `test_06_filtros_paginacao.py`

**Objetivo:** Validar filtros e navegação entre páginas.

### Testes

| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_01_filtro_canal_sac` | ✅ PASS | Filtro por "SAC" funciona |
| `test_02_filtro_canal_ouvidoria` | ✅ PASS | Filtro por "Ouvidoria" funciona |
| `test_03_filtro_urgencia_alta` | ✅ PASS | Filtro por urgência "Alta" funciona |
| `test_04_filtro_urgencia_critica` | ✅ PASS | Filtro por urgência "Crítica" funciona |
| `test_05_filtro_status_resolvida` | ✅ PASS | Filtro por status "Resolvida" funciona |
| `test_06_filtro_status_analise` | ❌ FAIL | URL encoding diferente (`+an%C3%A1lise`) |
| `test_07_texto_filtros_ativos` | ✅ PASS | Texto "Filtros aplicados" exibido |
| `test_08_limpar_filtros_remove_parametros` | ✅ PASS | "Limpar Filtros" remove query params |
| `test_09_limpar_filtros_restaura_exibicao` | ✅ PASS | Exibição volta ao normal |
| `test_10_filtro_sem_resultado` | ✅ PASS | Filtro com 0 resultados trata corretamente |
| `test_11_paginacao_visivel` | ✅ PASS | Controles de paginação visíveis |
| `test_12_pagina_atual_numero_1` | ✅ PASS | Página 1 está ativa na primeira visita |
| `test_13_link_proxima_navega` | ✅ PASS | Link "Próxima" navega para página 2 |
| `test_14_registros_pagina_2_diferentes` | ✅ PASS | Registros página 2 ≠ página 1 |
| `test_15_filtro_preservado_na_paginacao` | ✅ PASS | Filtro mantido ao navegar páginas |

---

## Suite 7: Dashboard (25 testes)

**Arquivo:** `test_07_dashboard.py`

**Objetivo:** Validar página de dashboard com KPIs e gráficos.

### Testes

| Teste | Status | Descrição |
|-------|--------|-----------|
| `test_01_acesso_dashboard` | ✅ PASS | Acesso via `/dashboard` funciona |
| `test_02_titulo_pagina` | ✅ PASS | Título "Dashboard" na aba |
| `test_03_header_visivel` | ✅ PASS | Header com navegação presente |
| `test_04_link_dashboard_ativo` | ✅ PASS | Link "Dashboard" destaque como ativo |
| `test_05_heading_dashboard` | ✅ PASS | Heading "Dashboard" presente |
| `test_06_kpi_cards_presentes` | ✅ PASS | Cards KPI estão visíveis |
| `test_07_kpi_valores_visiveis` | ✅ PASS | Valores dos KPIs preenchidos |
| `test_08_graficos_presentes` | ✅ PASS | Canvas gráficos carregam |
| `test_09_tabela_dados_presente` | ✅ PASS | Tabela de dados exibida |
| `test_10_tabela_tem_linhas` | ✅ PASS | Tabela contém registros |
| `test_11_tabela_headers_visiveis` | ✅ PASS | Headers da tabela presentes |
| `test_12_badges_status_visiveis` | ✅ PASS | Badges de status na tabela |
| `test_13_container_responsivo` | ✅ PASS | Container responsivo estruturado |
| `test_14_footer_visivel` | ✅ PASS | Footer presente no dashboard |
| `test_15_link_nova_reclamacao_presente` | ✅ PASS | Link para nova reclamação presente |
| `test_16_badge_live_presente` | ✅ PASS | Badge "Live" com pulse animation |
| `test_17_kpi_trending_info` | ✅ PASS | Informações de trending nos KPIs |
| `test_18_responsividade_mobile` | ✅ PASS | Layout responsivo em mobile |
| `test_19_grid_layout_kpi` | ✅ PASS | Grid layout dos KPIs correto |
| `test_20_chart_canvas_renderizado` | ✅ PASS | Canvas dos gráficos renderizado |
| `test_21_dados_tabela_nao_vazio` | ✅ PASS | Dados da tabela não vazios |
| `test_22_link_reclamacoes_funciona` | ✅ PASS | Link para lista funciona |
| `test_23_volta_para_dashboard` | ✅ PASS | Volta para dashboard funciona |
| `test_24_titulo_kpi_legivel` | ✅ PASS | Títulos dos KPIs legíveis |
| `test_25_styling_aplicado` | ✅ PASS | CSS aplicado corretamente |

---

## Prioridade de Testes

| Prioridade | Suite | Razão |
|-----------|-------|-------|
| P1 | Suite 2 | Fluxo principal — criação com agente IA |
| P1 | Suite 3 | Valida resultado da classificação |
| P2 | Suite 4 | Operação diária do operador |
| P2 | Suite 1 | Porta de entrada da aplicação |
| P3 | Suite 5 | Ação destrutiva — cobre edge cases |
| P3 | Suite 6 | Navegação e busca avançada |
| P3 | Suite 7 | Visualização de dados agregados |

---

## Próximos Passos

### Curto prazo (esta semana)
- [ ] Corrigir testes falhando
- [ ] Validar seletores CSS
- [ ] Verificar encoding de URLs

### Médio prazo (próximo mês)
- [ ] Adicionar testes de performance
- [ ] Integração com CI/CD
- [ ] Relatórios automáticos

### Longo prazo (roadmap)
- [ ] Testes de carga
- [ ] Testes de acessibilidade
- [ ] Testes móveis avançados
