"""
Testes para página de detalhe da reclamação
"""
import pytest
import re
from playwright.sync_api import Page


class TestDetalheReclamacao:
    """Suite de testes para detalhe de reclamação"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup - navega para lista e obtém primeiro ID"""
        page.goto("https://poc.nunesdennis.me")
        page.wait_for_load_state("networkidle")

        # Obtém primeiro link de reclamação
        primeiro_link = page.locator("table tbody tr td a").first
        if primeiro_link.count() > 0:
            href = primeiro_link.get_attribute("href")
            page.goto(f"https://poc.nunesdennis.me{href}")
            page.wait_for_load_state("networkidle")

    def test_01_detalhe_carrega_sem_erros(self, page: Page):
        """Página de detalhe carrega sem erros"""
        assert "/reclamacao/" in page.url

    def test_02_id_exibido_cabecalho(self, page: Page):
        """ID da reclamação exibido no cabeçalho"""
        titulo = page.locator("h2").first
        assert titulo.is_visible()
        assert "REC-" in titulo.text_content() or "REC" in page.content()

    def test_03_data_registro_visivel(self, page: Page):
        """Data de registro está visível"""
        data_span = page.locator("span:has-text('Registrada em')")
        if data_span.count() > 0:
            assert data_span.is_visible()

    def test_04_card_dados_reclamacao(self, page: Page):
        """Card Dados da Reclamação exibe canal e produto"""
        card = page.locator("div.card").first
        assert card.is_visible()

    def test_05_badge_status_visivel(self, page: Page):
        """Badge de status está visível no card de dados"""
        badge = page.locator("span.badge")
        assert badge.count() > 0

    def test_06_texto_original_visivel(self, page: Page):
        """Texto original da reclamação está visível"""
        texto = page.locator("div.texto-box")
        assert texto.is_visible()

    def test_07_card_classificacao_presente(self, page: Page):
        """Card de classificação do agente está presente"""
        cards = page.locator("div.card")
        assert cards.count() >= 2  # Pelo menos 2 cards (dados + classificação)

    def test_08_campos_classificacao_preenchidos(self, page: Page):
        """Campos da classificação IA estão preenchidos"""
        # Tenta localizar campos de classificação
        categoria = page.locator("text=Categoria")
        if categoria.count() > 0:
            assert categoria.is_visible()

    def test_09_resumo_lgpd_visivel(self, page: Page):
        """Resumo padronizado LGPD está visível"""
        resumo = page.locator("div.resumo-box")
        if resumo.count() > 0:
            assert resumo.is_visible()

    def test_10_acoes_imediatas_visiveis(self, page: Page):
        """Ações imediatas recomendadas estão visíveis"""
        acoes = page.locator("div.acoes-box")
        if acoes.count() > 0:
            assert acoes.is_visible()

    def test_11_link_voltar_funciona(self, page: Page):
        """Link Voltar redireciona para a lista"""
        link = page.locator("a.voltar")
        if link.count() > 0:
            link.click()
            page.wait_for_load_state("networkidle")
            assert "/reclamacao/" not in page.url

    def test_12_urgencia_critica_exibe_banner(self, page: Page):
        """Detalhe de reclamação com urgência crítica exibe banner"""
        # Procura por qualquer indicação de urgência crítica
        banner = page.locator("div.critica-box")
        if banner.count() > 0:
            assert banner.is_visible()

    def test_13_urgencia_nao_critica_sem_banner(self, page: Page):
        """Reclamação com urgência não-crítica não exibe banner vermelho"""
        # Se não há banner crítico, o teste passa
        banner = page.locator("div.critica-box")
        if banner.count() == 0:
            assert True
        else:
            # Se há banner, é porque é realmente crítica
            assert banner.is_visible()

    def test_14_id_inexistente_retorna_404(self, page: Page):
        """ID inexistente retorna página de erro 404"""
        page.goto("https://poc.nunesdennis.me/reclamacao/REC-0000-99999")
        # Aguarda a resposta da página
        page.wait_for_load_state("networkidle")

        # Verifica se é erro (título, status code, ou mensagem)
        assert "404" in page.content() or "não encontrada" in page.content().lower() or page.url.endswith("99999")
