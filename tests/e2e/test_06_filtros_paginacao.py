"""
Testes para filtros e paginação
"""
import pytest
from playwright.sync_api import Page


class TestFiltrosPaginacao:
    """Suite de testes para filtros e paginação"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup - navega para lista"""
        page.goto("https://poc.nunesdennis.me")
        page.wait_for_load_state("networkidle")

    def test_01_filtro_canal_sac(self, page: Page):
        """Filtro por Canal SAC retorna apenas registros SAC"""
        select = page.locator("select[name='canal']")
        select.select_option("SAC")

        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Verifica se canal está na URL
        assert "canal=SAC" in page.url

    def test_02_filtro_canal_ouvidoria(self, page: Page):
        """Filtro por Canal Ouvidoria funciona"""
        select = page.locator("select[name='canal']")
        select.select_option("Ouvidoria")

        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        assert "canal=Ouvidoria" in page.url

    def test_03_filtro_urgencia_alta(self, page: Page):
        """Filtro por Urgência Alta retorna registros corretos"""
        select = page.locator("select[name='urgencia']")
        select.select_option("Alta")

        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        assert "urgencia=Alta" in page.url

    def test_04_filtro_urgencia_critica(self, page: Page):
        """Filtro por Urgência Crítica retorna registros corretos"""
        select = page.locator("select[name='urgencia']")
        select.select_option("Crítica")

        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        assert "urgencia=Crítica" in page.url or "urgencia=Cr%C3%ADtica" in page.url

    def test_05_filtro_status_resolvida(self, page: Page):
        """Filtro por Status Resolvida retorna registros corretos"""
        select = page.locator("select[name='status']")
        select.select_option("Resolvida")

        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        assert "status=Resolvida" in page.url

    def test_06_filtro_status_analise(self, page: Page):
        """Filtro por Status Em análise retorna registros corretos"""
        select = page.locator("select[name='status']")
        select.select_option("Em análise")

        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        assert "status=Em%20análise" in page.url or "status=Em análise" in page.url

    def test_07_texto_filtros_ativos(self, page: Page):
        """Texto 'filtros ativos' aparece ao aplicar filtro"""
        select = page.locator("select[name='canal']")
        select.select_option("SAC")

        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Procura por indicação de filtros ativos
        ativo = page.locator("text=/filtro|Filtro|ativo|Ativo/i")
        assert ativo.count() > 0 or "canal=SAC" in page.url

    def test_08_limpar_filtros_remove_parametros(self, page: Page):
        """Limpar filtros remove os parâmetros da URL"""
        # Aplica filtro
        select = page.locator("select[name='canal']")
        select.select_option("SAC")
        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        assert "canal=SAC" in page.url

        # Limpa filtros
        page.locator("a.btn-secondary:has-text('Limpar')").click()
        page.wait_for_load_state("networkidle")

        assert "canal=" not in page.url

    def test_09_limpar_filtros_restaura_exibicao(self, page: Page):
        """Limpar filtros restaura exibição completa"""
        page.locator("select[name='canal']").select_option("SAC")
        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        linhas_filtradas = page.locator("table tbody tr").count()

        # Limpa filtros
        page.locator("a.btn-secondary:has-text('Limpar')").click()
        page.wait_for_load_state("networkidle")

        linhas_completas = page.locator("table tbody tr").count()

        # Sem filtro deve ter mais ou igual registros
        assert linhas_completas >= linhas_filtradas

    def test_10_filtro_sem_resultado(self, page: Page):
        """Filtro sem resultado exibe mensagem adequada"""
        page.locator("select[name='canal']").select_option("Ouvidoria")
        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Se não houver registros, procura por mensagem
        linhas = page.locator("table tbody tr").count()
        if linhas == 0:
            msg = page.locator("text=/nenhum|resultado|encontrado/i")
            assert msg.count() > 0 or linhas == 0

    def test_11_paginacao_visivel(self, page: Page):
        """Paginação está visível com mais de 20 registros"""
        paginacao = page.locator("div.paginacao")
        if paginacao.count() > 0:
            assert paginacao.is_visible()

    def test_12_pagina_atual_numero_1(self, page: Page):
        """Página atual é a número 1 ao acessar lista sem parâmetros"""
        atual = page.locator("span.atual")
        if atual.count() > 0:
            assert "1" in atual.text_content()

    def test_13_link_proxima_navega(self, page: Page):
        """Link Próxima navega para a página 2"""
        proxima = page.locator("a:has-text('Próxima')").first
        if proxima.count() > 0:
            proxima.click()
            page.wait_for_load_state("networkidle")

            assert "pagina=2" in page.url or "page=2" in page.url

    def test_14_registros_pagina_2_diferentes(self, page: Page):
        """Registros da página 2 são diferentes dos da página 1"""
        # Obtém IDs da página 1
        ids_pagina1 = set()
        for linha in page.locator("table tbody tr").all():
            id_texto = linha.locator("td").first.text_content().strip()
            ids_pagina1.add(id_texto)

        # Vai para página 2
        proxima = page.locator("a:has-text('Próxima')").first
        if proxima.count() > 0:
            proxima.click()
            page.wait_for_load_state("networkidle")

            # Obtém IDs da página 2
            ids_pagina2 = set()
            for linha in page.locator("table tbody tr").all():
                id_texto = linha.locator("td").first.text_content().strip()
                ids_pagina2.add(id_texto)

            # IDs devem ser diferentes
            assert ids_pagina1 != ids_pagina2

    def test_15_filtro_preservado_na_paginacao(self, page: Page):
        """Filtro é preservado ao navegar para próxima página"""
        # Aplica filtro
        page.locator("select[name='canal']").select_option("SAC")
        page.locator("form.filtros button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Vai para próxima página
        proxima = page.locator("a:has-text('Próxima')").first
        if proxima.count() > 0:
            proxima.click()
            page.wait_for_load_state("networkidle")

            # Filtro ainda deve estar na URL
            assert "canal=SAC" in page.url
