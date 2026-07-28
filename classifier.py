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
rigorosamente a Política Interna.
Sua função é analisar reclamações de clientes e retornar uma classificação estruturada usando exclusivamente
as regras da Política Interna POL-SAC-001 v2.0 fornecida no contexto.

INSTRUÇÕES IMPORTANTES:
- Sempre consulte a politica antes de classificar.
- Considere o documento da política interna como a única fonte de verdade.
- Não use conhecimento prévio, suposições ou regras externas.
- Se uma regra ou valor não estiver explícito na política, escolha a opção mais conservadora e use o valor mais próximo disponível.
- A resposta deve seguir estritamente o formato JSON solicitado.
- Não invente informações que não estejam presentes na política.
- Utilize do texto da reclamação para determinar os campos faltantes, caso um campo inserido pelo usuário como por exemplo canal de atendimento, não esteja de acordo com o texto, faça essa referencia no resumo, mas não altere o campo canal, apenas o resumo.
- Os prazos devem ser determinados de acordo com o produto seguindo a politica interna.
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

 

def classificar(texto_reclamacao: str, canal: str, produto: Optional[str] = None, multiplas_ocorrencias: bool = False, contexto: str = "") -> dict:
    """
    Classifica uma reclamação usando a Claude API, seguindo as regras da POL-SAC-001.

    Retorna dict com: categoria, produto, sentimento, urgencia, resumo,
    acoes_imediatas, responsavel, prazo_resposta.
    Em caso de falha na API, aplica classificação de fallback por regras locais.
    """
    prompt_usuario = f"""Canal de origem: {canal}
Produto informado pelo cliente: {produto or "Não informado"}
Múltiplas ocorrências relatadas pelo cliente: {"Sim — o cliente informou que já ocorreu mais de uma vez" if multiplas_ocorrencias else "Não informado"}
Contexto relevante:
{contexto}
Texto da reclamação:
{texto_reclamacao}"""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY não configurada. Usando fallback local.")
        return _classificar_fallback(texto_reclamacao, canal, produto, multiplas_ocorrencias)

    try:
        import httpx
        http_client = httpx.Client(verify=False)
        client = anthropic.Anthropic(api_key=api_key, http_client=http_client)


        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": prompt_usuario
                }
            ],
        )
        conteudo = message.content[0].text.strip()

        print ("Resposta da API Claude:", conteudo)  # Log para depuração
        # Remove blocos markdown se o modelo os incluir
        if conteudo.startswith("```"):
            conteudo = re.sub(r"^```(?:json)?\n?", "", conteudo)
            conteudo = re.sub(r"\n?```$", "", conteudo)

        resultado = json.loads(conteudo)
        resultado["resumo"] = _sanitize_resumo(resultado.get("resumo", ""))
        return resultado

    except Exception as e:
        import traceback
        print("ERRO ao classificar via API Claude:", e)
        traceback.print_exc()
        return _classificar_fallback(texto_reclamacao, canal, produto, multiplas_ocorrencias, data_ocorrencia)


def _classificar_fallback(texto: str, canal: str, produto: Optional[str], multiplas_ocorrencias: bool = False, data_ocorrencia: Optional[str] = None) -> dict:
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
    if any(p in texto_lower for p in ["fraude", "processo", "advogado", "ação judicial", "desesperado", "roubado", "absurdo", "vergonha", "inadmissível", "escândalo"]):
        sentimento = "Crítico"
    elif any(p in texto_lower for p in ["insatisfeito", "decepcionado", "péssimo", "horrível", "nunca mais", "indignado", "absurdo", "revoltado", "ninguém resolve", "cansado"]):
        sentimento = "Negativo"
    elif any(p in texto_lower for p in ["obrigado", "agradecido", "excelente", "ótimo", "parabéns", "elogio", "satisfeito", "muito bom", "adorei", "recomendo"]):
        sentimento = "Positivo"
    elif any(p in texto_lower for p in ["dúvida", "gostaria de saber", "poderia me informar", "gostaria de entender", "queria saber", "informação", "esclarecer"]):
        sentimento = "Neutro"
    elif any(p in texto_lower for p in ["reclamação", "problema", "erro", "falha", "não funciona", "cobrado", "cobrança"]):
        sentimento = "Negativo"
    else:
        sentimento = "Neutro"

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

    reincidencia_info = "Trata-se de ocorrência reincidente, o que eleva a prioridade de atendimento. " if multiplas_ocorrencias else ""
    data_info = f"Data da ocorrência: {data_ocorrencia}. " if data_ocorrencia else ""
    resumo = (
        f"Reclamação recebida via {canal} classificada como {categoria}. "
        f"{data_info}"
        f"{reincidencia_info}"
        f"Urgência {urgencia} aplicada conforme POL-SAC-001. "
        f"Encaminhar para {responsavel} no prazo de {prazo}."
    )

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
