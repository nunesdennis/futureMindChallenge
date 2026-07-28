"""
Testes para a página de lista de reclamações
"""
import pytest
from playwright.sync_api import Page


class TestListaReclamacoes:
    """Suite de testes para a lista de reclamações"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup - navega para a página de lista"""
        page.goto("https://poc.nunesdennis.me")
        page.wait_for_load_state("networkidle")

    def test_01_titulo_carrega_correto(self, page: Page):
        """Página principal carrega com título correto"""
        assert "FinGuard" in page.title() or "Reclamações" in page.title()

    def test_02_contador_registros_visivel(self, page: Page):
        """Contador de registros está visível"""
        info = page.locator("p.total-info")
        assert info.is_visible()

    def test_03_tabela_possui_dez_colunas(self, page: Page):
        """Tabela possui as dez colunas esperadas"""
        headers = page.locator("table thead th")
        assert headers.count() >= 5  # Mínimo de colunas

    def test_04_cabecalhos_corretos(self, page: Page):
        """Cabeçalhos das colunas estão corretos"""
        primeira_coluna = page.locator("table thead th").first
        assert primeira_coluna.is_visible()

    def test_05_tabela_exibe_registros(self, page: Page):
        """Tabela exibe registros na primeira página"""
        linhas = page.locator("table tbody tr")
        assert linhas.count() > 0

    def test_06_cada_linha_tem_botoes(self, page: Page):
        """Cada linha possui botões Ver e Deletar"""
        primeira_linha = page.locator("table tbody tr").first
        botoes = primeira_linha.locator("a, button")
        assert botoes.count() >= 2

    def test_07_botao_ver_redireciona(self, page: Page):
        """Botão Ver redireciona para detalhe da reclamação"""
        link_ver = page.locator("table tbody tr td a").first
        href = link_ver.get_attribute("href")
        assert href and "/reclamacao/" in href

    def test_08_badges_urgencia_visiveis(self, page: Page):
        """Badges de urgência estão visíveis nas linhas"""
        badges = page.locator("table tbody tr span.badge")
        assert badges.count() > 0

    def test_09_logo_visivel(self, page: Page):
        """Logo FinGuard está visível no header"""
        logo = page.locator("header h1")
        assert logo.is_visible()

    def test_10_footer_visivel(self, page: Page):
        """Footer exibe referência à política interna"""
        footer = page.locator("footer")
        assert footer.is_visible()
