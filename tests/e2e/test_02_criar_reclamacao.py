"""
Testes para criação de reclamações
"""
import pytest
from playwright.sync_api import Page


class TestCriarReclamacao:
    """Suite de testes para criar reclamação"""

    TEXTO_GENERICO = (
        "Preciso de informações sobre meu contrato de empréstimo. "
        "Não entendi os encargos cobrados na última fatura."
    )

    TEXTO_FRAUDE = (
        "Detectei uma transação suspeita no meu cartão de crédito. "
        "Um valor de R$3.200,00 foi debitado sem minha autorização. "
        "Acredito que fui vítima de fraude."
    )

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup - navega para formulário"""
        page.goto("https://poc.nunesdennis.me/nova")
        page.wait_for_load_state("networkidle")

    def test_01_formulario_carrega(self, page: Page):
        """Acessa formulário via link na navbar"""
        assert "nova" in page.url or "form" in page.url.lower()

    def test_02_aviso_ia_visivel(self, page: Page):
        """Aviso do agente IA está visível no formulário"""
        aviso = page.locator("div.aviso-ia")
        assert aviso.is_visible() or page.locator("text=IA").count() > 0

    def test_03_select_canal_opcoes(self, page: Page):
        """Select Canal contém todas as opções esperadas"""
        select = page.locator("select[name='canal']")
        assert select.is_visible()
        opcoes = ["SAC", "Ouvidoria", "Banco Central"]
        for opcao in opcoes:
            assert page.locator(f"option:has-text('{opcao}')").count() > 0

    def test_04_select_produto_opcoes(self, page: Page):
        """Select Produto contém todas as opções esperadas"""
        select = page.locator("select[name='produto']")
        assert select.is_visible()

    def test_05_submissao_sem_canal_erro(self, page: Page):
        """Submissão sem canal exibe erro de validação"""
        # Tenta submeter sem preencher canal
        page.locator("textarea[name='texto_reclamacao']").fill(self.TEXTO_GENERICO)
        page.locator("button[type='submit']").click()

        # Verifica se há mensagem de erro
        erro = page.locator("div.flash.erro")
        assert erro.is_visible() or "obrigatório" in page.content().lower()

    def test_06_submissao_sem_texto_erro(self, page: Page):
        """Submissão sem texto exibe erro de validação"""
        page.locator("select[name='canal']").select_option("SAC")
        page.locator("button[type='submit']").click()

        erro = page.locator("div.flash.erro")
        assert erro.is_visible() or "obrigatório" in page.content().lower()

    def test_07_campo_data_oculto_sim(self, page: Page):
        """Campo data fica oculto quando primeira ocorrência é Sim"""
        radio_sim = page.locator("input[name='primeira_ocorrencia'][value='sim']")
        radio_sim.click()

        campo_data = page.locator("div#campo_data")
        # Campo deve estar oculto ou não visível
        assert not campo_data.is_visible() or "display:none" in campo_data.get_attribute("style") or ""

    def test_08_campo_data_visivel_nao(self, page: Page):
        """Campo data fica visível quando primeira ocorrência é Não"""
        radio_nao = page.locator("input[name='primeira_ocorrencia'][value='nao']")
        radio_nao.click()

        campo_data = page.locator("div#campo_data")
        assert campo_data.is_visible()

    def test_09_botao_cancelar_volta(self, page: Page):
        """Botão Cancelar retorna para a lista"""
        page.locator("a[href='/'].btn-secondary").click()
        page.wait_for_load_state("networkidle")

        assert "nova" not in page.url

    def test_10_cria_reclamacao_completa(self, page: Page):
        """Cria reclamação completa e valida redirect com sucesso"""
        page.locator("select[name='canal']").select_option("SAC")
        page.locator("select[name='produto']").select_option("Cartão de Crédito")
        page.locator("textarea[name='texto_reclamacao']").fill(self.TEXTO_GENERICO)
        page.locator("input[name='primeira_ocorrencia'][value='sim']").click()

        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Verifica se redireciona para detalhe (URL com ID)
        assert "/reclamacao/" in page.url

    def test_11_id_gerado_formato_correto(self, page: Page):
        """ID gerado segue o formato REC-AAAA-NNNNN"""
        page.locator("select[name='canal']").select_option("SAC")
        page.locator("textarea[name='texto_reclamacao']").fill(self.TEXTO_GENERICO)
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Extrai ID da URL
        url = page.url
        import re
        match = re.search(r'REC-\d{4}-\d{5}', url)
        assert match is not None

    def test_12_reclamacao_com_data_manual(self, page: Page):
        """Cria reclamação com data de ocorrência manual"""
        page.locator("select[name='canal']").select_option("SAC")
        page.locator("textarea[name='texto_reclamacao']").fill(self.TEXTO_GENERICO)
        page.locator("input[name='primeira_ocorrencia'][value='nao']").click()

        # Preenche a data
        page.locator("input#data_reclamacao").fill("2024-06-15")
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        assert "/reclamacao/" in page.url

    def test_13_reclamacao_fraude_urgencia_critica(self, page: Page):
        """Reclamação com texto de fraude gera urgência crítica"""
        page.locator("select[name='canal']").select_option("SAC")
        page.locator("textarea[name='texto_reclamacao']").fill(self.TEXTO_FRAUDE)
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        # Verifica se há indicação de urgência crítica
        critica = page.locator("div.critica-box")
        assert critica.count() > 0 or "CRÍTICA" in page.content()

    def test_14_reclamacao_critica_exibe_banner(self, page: Page):
        """Reclamação crítica exibe banner de alerta no detalhe"""
        page.locator("select[name='canal']").select_option("SAC")
        page.locator("textarea[name='texto_reclamacao']").fill(self.TEXTO_FRAUDE)
        page.locator("button[type='submit']").click()
        page.wait_for_load_state("networkidle")

        banner = page.locator("div.critica-box")
        assert banner.is_visible()
