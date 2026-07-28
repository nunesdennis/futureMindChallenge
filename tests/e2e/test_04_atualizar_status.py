"""
Testes para atualizar status de reclamação
"""
import pytest
from playwright.sync_api import Page


class TestAtualizarStatus:
    """Suite de testes para atualizar status"""

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

    def test_01_formulario_status_presente(self, page: Page):
        """Formulário de status está presente na página de detalhe"""
        form = page.locator("form.status-form")
        assert form.count() > 0

    def test_02_select_status_tres_opcoes(self, page: Page):
        """Select de status contém as três opções"""
        select = page.locator("select[name='status']")
        assert select.is_visible()

        opcoes = ["Aberta", "Em análise", "Resolvida"]
        for opcao in opcoes:
            assert page.locator(f"option:has-text('{opcao}')").count() > 0

    def test_03_status_atual_pre_selecionado(self, page: Page):
        """Status atual está pré-selecionado"""
        select = page.locator("select[name='status']")
        valor = select.input_value()
        assert valor is not None and valor != ""

    def test_04_botao_atualizar_presente(self, page: Page):
        """Botão Atualizar status está presente"""
        botao = page.locator("form.status-form button[type='submit']")
        assert botao.is_visible()

    def test_05_cancelar_confirmar_fecha(self, page: Page):
        """Cancelar confirmação não altera status"""
        # Muda status
        select = page.locator("select[name='status']")
        opcoes_atuais = select.locator("option").all()
        if len(opcoes_atuais) > 1:
            select.select_option(opcoes_atuais[1].get_attribute("value"))

            # Captura status anterior
            status_novo = select.input_value()

            # Clica em atualizar
            page.locator("form.status-form button[type='submit']").click()

            # Se houve diálogo de confirmação, cancela
            page.on("dialog", lambda dialog: dialog.dismiss())
            page.wait_for_load_state("networkidle")

    def test_06_altera_status_analise_sucesso(self, page: Page):
        """Altera status para Em análise com sucesso"""
        select = page.locator("select[name='status']")
        select.select_option("Em análise")

        page.locator("form.status-form button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Verifica se há mensagem de sucesso
        sucesso = page.locator("div.flash.sucesso")
        assert sucesso.count() > 0 or "sucesso" in page.content().lower()

    def test_07_altera_status_volta_aberta(self, page: Page):
        """Altera status de volta para Aberta com sucesso"""
        select = page.locator("select[name='status']")
        select.select_option("Aberta")

        page.locator("form.status-form button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        sucesso = page.locator("div.flash.sucesso")
        assert sucesso.count() > 0 or "sucesso" in page.content().lower()
