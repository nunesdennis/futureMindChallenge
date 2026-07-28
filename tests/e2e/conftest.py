import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "https://poc.nunesdennis.me"


@pytest.fixture(scope="function")
def browser_context():
    """Fixture que fornece browser context para cada teste"""
    with sync_playwright() as p:
        # Abrir browser sem headless para permitir login manual
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = browser.new_context()
        page = context.new_page()

        page.goto(BASE_URL, wait_until="networkidle")

        yield page, context, browser

        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """Fixture simplificada que retorna apenas a página"""
    page, context, browser = browser_context
    return page
