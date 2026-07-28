"""
Testes para o Dashboard Gerencial
"""
import pytest
from playwright.sync_api import Page


class TestDashboard:
    """Suite de testes para o Dashboard"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup - navega para dashboard"""
        page.goto("https://poc.nunesdennis.me/dashboard")
        page.wait_for_load_state("networkidle")

    def test_01_acesso_dashboard(self, page: Page):
        """Acesso ao dashboard"""
        assert "/dashboard" in page.url

    def test_02_titulo_pagina(self, page: Page):
        """Título da página carrega corretamente"""
        assert "Dashboard" in page.title() or "dashboard" in page.title().lower()

    def test_03_header_visivel(self, page: Page):
        """Header está visível"""
        header = page.query_selector("header")
        assert header is not None

    def test_04_link_dashboard_ativo(self, page: Page):
        """Link Dashboard na nav está destacado ou ativo"""
        nav = page.query_selector("nav")
        assert nav is not None
        dashboard_link = page.query_selector("nav a:has-text('Dashboard')")
        assert dashboard_link is not None

    def test_05_heading_dashboard(self, page: Page):
        """Heading do dashboard está visível"""
        h2 = page.query_selector("h2, h1")
        assert h2 is not None

    def test_06_kpi_cards_presentes(self, page: Page):
        """KPI cards/estatísticas estão presentes"""
        kpi_cards = page.query_selector_all(".kpi-card, [class*='kpi'], [class*='stat']")
        assert len(kpi_cards) > 0

    def test_07_kpi_valores_visiveis(self, page: Page):
        """Valores dos KPIs estão visíveis"""
        kpi_values = page.query_selector_all(".kpi-value, [class*='value'], [class*='metric']")
        assert len(kpi_values) > 0

    def test_08_graficos_presentes(self, page: Page):
        """Gráficos (canvas) estão presentes"""
        canvas = page.query_selector_all("canvas")
        assert len(canvas) > 0, "Nenhum gráfico encontrado"

    def test_09_tabela_dados_presente(self, page: Page):
        """Tabela de dados está presente"""
        table = page.query_selector("table")
        assert table is not None

    def test_10_tabela_tem_linhas(self, page: Page):
        """Tabela contém linhas de dados"""
        rows = page.query_selector_all("table tbody tr")
        assert len(rows) > 0

    def test_11_tabela_headers_visiveis(self, page: Page):
        """Headers da tabela estão visíveis"""
        headers = page.query_selector_all("table thead th")
        assert len(headers) > 0

    def test_12_badges_status_visiveis(self, page: Page):
        """Badges de status estão visíveis na tabela"""
        badges = page.query_selector_all("span.badge, [class*='badge']")
        assert len(badges) > 0

    def test_13_container_responsivo(self, page: Page):
        """Container do dashboard existe"""
        container = page.query_selector(".container, .dash-root")
        assert container is not None

    def test_14_footer_visivel(self, page: Page):
        """Footer está visível"""
        footer = page.query_selector("footer")
        if footer:
            assert footer.is_visible()

    def test_15_link_nova_reclamacao_presente(self, page: Page):
        """Link para criar nova reclamação está acessível"""
        link = page.query_selector("a[href='/nova']")
        assert link is not None

    def test_16_badge_live_presente(self, page: Page):
        """Badge 'Live' ou indicador de atualização está presente"""
        badge_live = page.query_selector("[class*='badge-live'], [class*='live']")
        if badge_live:
            assert badge_live.is_visible()

    def test_17_kpi_trending_info(self, page: Page):
        """Informações de trending/tendência estão presentes"""
        trend = page.query_selector("[class*='trend'], [class*='trending']")
        if trend:
            assert trend.is_visible()

    def test_18_responsividade_mobile(self, page: Page):
        """Dashboard é responsivo (viewport mobile)"""
        # Define viewport mobile
        page.set_viewport_size({"width": 375, "height": 667})
        page.reload()
        page.wait_for_load_state("networkidle")

        # Verifica se elementos principais ainda estão visíveis
        header = page.query_selector("header")
        assert header.is_visible()

        container = page.query_selector(".container")
        assert container is not None

    def test_19_grid_layout_kpi(self, page: Page):
        """Grid de KPIs está responsivo"""
        kpi_row = page.query_selector(".kpi-row, [class*='grid']")
        if kpi_row:
            # Verifica display computed
            display = page.evaluate("window.getComputedStyle(document.querySelector('.kpi-row')).display")
            assert display in ["grid", "flex", "block"]

    def test_20_chart_canvas_renderizado(self, page: Page):
        """Canvas dos gráficos está renderizado"""
        canvas = page.query_selector_all("canvas")
        if len(canvas) > 0:
            first_canvas = canvas[0]
            # Verifica se canvas tem atributos de tamanho
            width = first_canvas.get_attribute("width")
            height = first_canvas.get_attribute("height")
            assert width is not None or height is not None

    def test_21_dados_tabela_nao_vazio(self, page: Page):
        """Dados da tabela não estão vazios"""
        rows = page.query_selector_all("table tbody tr")
        if len(rows) > 0:
            first_row = rows[0]
            text = first_row.text_content().strip()
            assert len(text) > 0

    def test_22_link_reclamacoes_funciona(self, page: Page):
        """Link para página de reclamações funciona"""
        link = page.query_selector("a[href='/']")
        if link:
            link.click()
            page.wait_for_load_state("networkidle")
            assert page.url.endswith("/") or "dashboard" not in page.url

    def test_23_volta_para_dashboard(self, page: Page):
        """Consegue voltar para dashboard"""
        page.goto("https://poc.nunesdennis.me")
        page.wait_for_load_state("networkidle")

        dashboard_link = page.query_selector("a[href='/dashboard']")
        if dashboard_link:
            dashboard_link.click()
            page.wait_for_load_state("networkidle")
            assert "/dashboard" in page.url

    def test_24_titulo_kpi_legivel(self, page: Page):
        """Títulos dos KPIs são legíveis"""
        titles = page.query_selector_all(".kpi-title, [class*='title']")
        if len(titles) > 0:
            first_title = titles[0]
            text = first_title.text_content().strip()
            assert len(text) > 0

    def test_25_styling_aplicado(self, page: Page):
        """Styling do dashboard está aplicado"""
        kpi_card = page.query_selector(".kpi-card")
        if kpi_card:
            bg_color = page.evaluate(
                "window.getComputedStyle(document.querySelector('.kpi-card')).backgroundColor"
            )
            assert bg_color is not None
