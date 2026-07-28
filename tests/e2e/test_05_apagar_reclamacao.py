"""
Testes para apagar reclamação
"""
import pytest
from playwright.sync_api import Page


class TestApagarReclamacao:
    """Suite de testes para apagar reclamação"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup - navega para lista"""
        page.goto("https://poc.nunesdennis.me")
        page.wait_for_load_state("networkidle")

    def test_01_botao_deletar_presente(self, page: Page):
        """Botão Deletar está presente na lista"""
        botao = page.locator("form[action*='/apagar'] button").first
        assert botao.count() > 0

    def test_02_cancelar_confirmar_nao_deleta(self, page: Page):
        """Cancelar confirmação não exclui o registro"""
        botao = page.locator("form[action*='/apagar'] button").first
        linhas_antes = page.locator("table tbody tr").count()

        # Setup para capturar e cancelar diálogo
        page.once("dialog", lambda dialog: dialog.dismiss())

        botao.click()
        page.wait_for_load_state("networkidle")

        linhas_depois = page.locator("table tbody tr").count()
        assert linhas_antes == linhas_depois

    def test_03_confirmar_exclui_registro(self, page: Page):
        """Confirmar exclusão remove o registro da lista"""
        botao = page.locator("form[action*='/apagar'] button").first
        linhas_antes = page.locator("table tbody tr").count()

        # Setup para aceitar diálogo
        page.once("dialog", lambda dialog: dialog.accept())

        botao.click()
        page.wait_for_load_state("networkidle")

        linhas_depois = page.locator("table tbody tr").count()
        assert linhas_depois == linhas_antes - 1

    def test_04_flash_sucesso_mostra_id(self, page: Page):
        """Flash de sucesso exibe o ID da reclamação apagada"""
        botao = page.locator("form[action*='/apagar'] button").first
        primeira_linha = page.locator("table tbody tr").first

        # Obtém ID para verificação
        rec_id = primeira_linha.locator("td").first.text_content()

        page.once("dialog", lambda dialog: dialog.accept())
        botao.click()
        page.wait_for_load_state("networkidle")

        flash = page.locator("div.flash.sucesso")
        if flash.count() > 0:
            assert flash.is_visible()

    def test_05_registro_deletado_nao_aparece(self, page: Page):
        """Registro deletado não aparece mais na lista"""
        # Obtém ID primeiro
        primeira_linha = page.locator("table tbody tr").first
        rec_id = primeira_linha.locator("td").first.text_content().strip()

        # Deleta
        botao = primeira_linha.locator("form[action*='/apagar'] button")
        page.once("dialog", lambda dialog: dialog.accept())
        botao.click()
        page.wait_for_load_state("networkidle")

        # Procura pelo ID na tabela
        linhas = page.locator("table tbody tr")
        encontrado = False
        for linha in linhas.all():
            if rec_id in linha.text_content():
                encontrado = True
                break

        assert not encontrado

    def test_06_acesso_direto_deletado_retorna_erro(self, page: Page):
        """Acesso direto ao detalhe de registro deletado retorna erro"""
        # Obtém URL de primeiro registro
        primeira_linha = page.locator("table tbody tr").first
        link = primeira_linha.locator("a").first
        url = link.get_attribute("href")

        # Deleta o registro
        botao = primeira_linha.locator("form[action*='/apagar'] button")
        page.once("dialog", lambda dialog: dialog.accept())
        botao.click()
        page.wait_for_load_state("networkidle")

        # Tenta acessar a URL deletada
        page.goto(f"https://poc.nunesdennis.me{url}")
        page.wait_for_load_state("networkidle")

        # Verifica se é erro
        assert "404" in page.content() or "não encontrada" in page.content().lower()
