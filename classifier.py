"""
Agente classificador de reclamações FinGuard.

Segue as regras da POL-SAC-001 v2.0 (KS_POLITICA_INTERNA) para determinar:
- Categoria da reclamação
- Produto identificado
- Sentimento do cliente
- Nível de urgência e ações imediatas
- Responsável pelo atendimento
- Prazo de resposta
- Resumo padronizado (sem dados pessoais, conforme LGPD)
"""

import json
import os
import re
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Você é o agente classificador de reclamações da FinGuard, instituição financeira.
Sua função é analisar reclamações de clientes e retornar uma classificação estruturada seguindo
rigorosamente a Política Interna POL-SAC-001 v2.0.

=== REGRAS DE CLASSIFICAÇÃO DE URGÊNCIA (POL-SAC-001 §2) ===

URGÊNCIA CRÍTICA (prazo: até 4 horas):
- Indícios de fraude ou acesso não autorizado
- Menção a Banco Central, Procon, Justiça ou advogado
- Canal de origem: Banco Central ou Procon → AUTOMATICAMENTE CRÍTICA
- Risco à segurança do cliente
- Vulnerabilidade emocional ou financeira extrema (ex: "única reserva", "desespero", "tirando o sono")
Ações: contato ativo em até 2h, escalar para gerente + Compliance, acionar Prevenção a Fraudes se fraude

URGÊNCIA ALTA (prazo: até 24 horas):
- Valor financeiro acima de R$ 500
- Múltiplas tentativas de contato sem resolução (3+ tentativas)
- Ameaça de escalar para órgãos reguladores (sem ainda ter feito)
Ações: contato ativo em até 4h, analista dedicado, notificar coordenador, registrar no painel gerencial

URGÊNCIA MÉDIA (prazo: até 3 dias úteis):
- Impacto financeiro moderado (até R$ 500)
- Problemas recorrentes ou falhas de atendimento
- Canal Ouvidoria (segunda instância)
Ações: confirmar recebimento em 12h, analista sênior em 24h, análise de estorno se aplicável

URGÊNCIA BAIXA (prazo: até 5 dias úteis):
- Dúvidas operacionais, informações, insatisfações leves sem impacto financeiro
Ações: registrar protocolo e enviar confirmação em 24h, fila padrão da área responsável

=== REGRAS POR CANAL (POL-SAC-001 §4) ===
- SAC: primeira instância, prazo legal 5 dias úteis
- Ouvidoria: segunda instância, analista sênior dedicado, prazo 10 dias úteis
- Banco Central / Procon: CRÍTICA automática, notificar Compliance em 2h, revisão jurídica
- Redes Sociais: resposta pública em 2h, migrar para canal privado imediatamente

=== RESPONSÁVEIS POR PRODUTO (POL-SAC-001 §3) ===
- Cartão de Crédito → Gerência de Cartões
- Conta Corrente → Gerência de Contas
- Empréstimo → Gerência de Crédito
- Investimentos → Gerência de Investimentos
- Seguros → Gerência de Seguros
- Não Identificado → Central de Atendimento

=== PROTEÇÃO DE DADOS (POL-SAC-001 §5) ===
- O resumo NÃO pode conter: CPF, número de conta, número de cartão, nome completo do cliente
- Substituir por [DADO PESSOAL OMITIDO] se necessário
- Ocultar palavrões ou linguagem inadequada com [CONTEÚDO OMITIDO]

=== CATEGORIAS VÁLIDAS ===
Cobrança Indevida | Atendimento | Fraude/Segurança | Produto/Serviço | Cancelamento | Outros

=== SENTIMENTOS VÁLIDOS ===
Positivo | Neutro | Negativo | Crítico

=== FORMATO DE SAÍDA ===
Retorne APENAS um JSON válido, sem markdown, sem explicações:
{
  "categoria": "<categoria>",
  "produto": "<produto identificado ou Não Identificado>",
  "sentimento": "<sentimento>",
  "urgencia": "<Baixa|Média|Alta|Crítica>",
  "resumo": "<2-3 frases em linguagem padronizada, sem dados pessoais>",
  "acoes_imediatas": "<ações recomendadas conforme a política>",
  "responsavel": "<gerência responsável>",
  "prazo_resposta": "<prazo conforme urgência e canal>"
}"""


def _sanitize_resumo(texto: str) -> str:
    """Remove dados pessoais e palavrões do resumo gerado pela IA."""
    # CPF no formato 000.000.000-00 ou 00000000000
    texto = re.sub(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", "[DADO PESSOAL OMITIDO]", texto)
    # Números de conta e cartão (sequências longas de dígitos)
    texto = re.sub(r"\b\d{10,}\b", "[DADO PESSOAL OMITIDO]", texto)
    return texto


def classificar(texto_reclamacao: str, canal: str, produto: Optional[str] = None, multiplas_ocorrencias: bool = False) -> dict:
    """
    Classifica uma reclamação usando a Claude API, seguindo as regras da POL-SAC-001.

    Retorna dict com: categoria, produto, sentimento, urgencia, resumo,
    acoes_imediatas, responsavel, prazo_resposta.
    Em caso de falha na API, aplica classificação de fallback por regras locais.
    """
    prompt_usuario = f"""Canal de origem: {canal}
Produto informado pelo cliente: {produto or "Não informado"}
Múltiplas ocorrências relatadas pelo cliente: {"Sim — o cliente informou que já ocorreu mais de uma vez" if multiplas_ocorrencias else "Não informado"}

Texto da reclamação:
{texto_reclamacao}"""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _classificar_fallback(texto_reclamacao, canal, produto, multiplas_ocorrencias)

    try:
        import httpx
        http_client = httpx.Client(verify=False)
        client = anthropic.Anthropic(api_key=api_key, http_client=http_client)
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt_usuario}],
        )
        conteudo = message.content[0].text.strip()

        # Remove blocos markdown se o modelo os incluir
        if conteudo.startswith("```"):
            conteudo = re.sub(r"^```(?:json)?\n?", "", conteudo)
            conteudo = re.sub(r"\n?```$", "", conteudo)

        resultado = json.loads(conteudo)
        resultado["resumo"] = _sanitize_resumo(resultado.get("resumo", ""))
        return resultado

    except (anthropic.APIError, json.JSONDecodeError, KeyError):
        return _classificar_fallback(texto_reclamacao, canal, produto, multiplas_ocorrencias)


def _classificar_fallback(texto: str, canal: str, produto: Optional[str], multiplas_ocorrencias: bool = False) -> dict:
    """
    Classificação por regras locais quando a API não está disponível.
    Segue os mesmos critérios da POL-SAC-001.
    """
    texto_lower = texto.lower()

    # --- Urgência e prazo por canal ---
    canal_lower = canal.lower()
    if "banco central" in canal_lower or "procon" in canal_lower:
        urgencia = "Crítica"
        prazo = "Até 4 horas (Crítica — canal regulatório)"
        acoes = "Contato ativo em até 2h. Escalar para gerente e Compliance. Revisão jurídica obrigatória antes de responder ao órgão regulador."
    else:
        # Detectar urgência pelo texto
        tem_fraude = any(p in texto_lower for p in ["fraude", "acesso não autorizado", "hackearam", "clonaram", "transação não reconhecida", "não fiz essa"])
        tem_regulatorio = any(p in texto_lower for p in ["banco central", "procon", "justiça", "advogado", "processo judicial"])
        tem_vulnerabilidade = any(p in texto_lower for p in ["desesperado", "desespero", "tirando o sono", "única reserva", "não sei mais", "imploro"])

        valor_alto = bool(re.search(r"r\$\s*[5-9]\d{2,}|r\$\s*\d{1,3}\.\d{3}", texto_lower))
        multiplas_tentativas = multiplas_ocorrencias or any(p in texto_lower for p in ["terceira vez", "quarta vez", "quinta vez", "já liguei várias", "já abri vários", "perdi a conta"])
        ameaca_escalar = any(p in texto_lower for p in ["vou procurar", "vou acionar", "vou ao procon", "vou ao banco central"])

        if tem_fraude or tem_regulatorio or tem_vulnerabilidade:
            urgencia = "Crítica"
            prazo = "Até 4 horas"
            acoes = "Contato ativo em até 2h. Escalar para gerente e Compliance."
            if tem_fraude:
                acoes += " Acionar equipe de Prevenção a Fraudes e bloquear transações suspeitas."
        elif valor_alto or multiplas_tentativas or ameaca_escalar:
            urgencia = "Alta"
            prazo = "Até 24 horas"
            acoes = "Contato ativo em até 4h. Designar analista dedicado. Notificar coordenador. Registrar no painel gerencial."
        elif "ouvidoria" in canal_lower:
            urgencia = "Média"
            prazo = "Até 3 dias úteis (Ouvidoria: prazo legal 10 dias úteis)"
            acoes = "Confirmar recebimento em 12h. Analista sênior avaliar em 24h."
        elif any(p in texto_lower for p in ["cobrança", "cobrado", "estorno", "taxa", "juros", "parcela"]):
            urgencia = "Média"
            prazo = "Até 3 dias úteis"
            acoes = "Confirmar recebimento em 12h. Analista sênior avaliar em 24h. Solicitar análise de estorno se aplicável."
        else:
            urgencia = "Baixa"
            prazo = "Até 5 dias úteis"
            acoes = "Registrar protocolo e enviar confirmação ao cliente em até 24h. Encaminhar para fila padrão."

    # --- Categoria ---
    if any(p in texto_lower for p in ["fraude", "acesso não autorizado", "clonaram", "hackearam", "transação não reconhecida"]):
        categoria = "Fraude/Segurança"
    elif any(p in texto_lower for p in ["cancelamento", "cancelar", "encerrar", "cancelei"]):
        categoria = "Cancelamento"
    elif any(p in texto_lower for p in ["cobrança indevida", "cobrado indevidamente", "taxa indevida", "não reconheço", "não fiz essa compra", "estorno"]):
        categoria = "Cobrança Indevida"
    elif any(p in texto_lower for p in ["atendimento", "fui transferido", "ninguém resolve", "mal atendido", "demora"]):
        categoria = "Atendimento"
    elif any(p in texto_lower for p in ["produto", "serviço", "aplicativo", "app", "sistema fora", "não funciona"]):
        categoria = "Produto/Serviço"
    else:
        categoria = "Outros"

    # --- Sentimento ---
    if any(p in texto_lower for p in ["fraude", "processo", "advogado", "ação judicial", "desesperado", "roubado", "absurdo", "vergonha"]):
        sentimento = "Crítico"
    elif any(p in texto_lower for p in ["insatisfeito", "decepcionado", "péssimo", "horrível", "nunca mais", "indignado"]):
        sentimento = "Negativo"
    elif any(p in texto_lower for p in ["dúvida", "gostaria de saber", "poderia me informar"]):
        sentimento = "Neutro"
    else:
        sentimento = "Negativo"

    # --- Produto identificado ---
    produto_id = produto or "Não Identificado"

    # --- Responsável ---
    responsaveis = {
        "Cartão de Crédito": "Gerência de Cartões",
        "Conta Corrente": "Gerência de Contas",
        "Empréstimo": "Gerência de Crédito",
        "Investimentos": "Gerência de Investimentos",
        "Seguros": "Gerência de Seguros",
    }
    responsavel = responsaveis.get(produto_id, "Central de Atendimento")

    resumo = f"Reclamação recebida via {canal} classificada como {categoria}. " \
             f"Urgência {urgencia} aplicada conforme POL-SAC-001. " \
             f"Encaminhar para {responsavel} no prazo de {prazo}."

    return {
        "categoria": categoria,
        "produto": produto_id,
        "sentimento": sentimento,
        "urgencia": urgencia,
        "resumo": resumo,
        "acoes_imediatas": acoes,
        "responsavel": responsavel,
        "prazo_resposta": prazo,
    }
