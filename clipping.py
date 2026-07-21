"""
Clipping de Imprensa - Renan Santos
Busca notícias em múltiplas fontes e retorna lista estruturada.
"""

import feedparser
import html
import re
import time

PESSOA = "Renan Santos"
TERMOS_BUSCA = [
    "renan santos",
    "renan santos mbl",
    "candidato renan",
    "pré-candidato renan",
    "partido missão",
    "missão renan",
]

FEEDS = {
    "Google News – Renan Santos": "https://news.google.com/rss/search?q=%22Renan+Santos%22&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Google News – Presidência": "https://news.google.com/rss/search?q=%22Renan+Santos%22+presid%C3%AAncia&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Google News – Partido Missão": "https://news.google.com/rss/search?q=%22Partido+Miss%C3%A3o%22&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Google News – MBL Renan": "https://news.google.com/rss/search?q=%22Renan+Santos%22+MBL&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "G1": "https://g1.globo.com/rss/g1/",
    "UOL": "https://rss.uol.com.br/feed/noticias.xml",
    "Folha de S.Paulo": "https://feeds.folha.uol.com.br/folha/poder/rss091.xml",
    "Estadão": "https://feeds.estadao.com.br/rss/politica",
    "Metrópoles": "https://www.metropoles.com/feed",
    "Correio Braziliense": "https://www.correiobraziliense.com.br/rss/feed/politica.xml",
    "Veja": "https://veja.abril.com.br/feed/",
}


def _limpar_html(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return html.unescape(texto)


def _menciona_renan(entry) -> bool:
    campos = [
        getattr(entry, "title", ""),
        getattr(entry, "summary", ""),
        getattr(entry, "description", ""),
    ]
    texto = " ".join(campos).lower()
    return any(t in texto for t in TERMOS_BUSCA)


def buscar_noticias() -> dict:
    """
    Retorna dict: { nome_fonte: [{ titulo, link, resumo, data }] }
    """
    resultados = {}
    for nome, url in FEEDS.items():
        try:
            bust = f"{'&' if '?' in url else '?'}_={int(time.time())}"
    feed = feedparser.parse(url + bust, request_headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"})
            entradas = []
            for entry in feed.entries:
                if _menciona_renan(entry):
                    entradas.append({
                        "titulo": _limpar_html(getattr(entry, "title", "Sem título")),
                        "link": getattr(entry, "link", "#"),
                        "resumo": _limpar_html(getattr(entry, "summary", getattr(entry, "description", ""))),
                        "data": getattr(entry, "published", ""),
                    })
            if entradas:
                resultados[nome] = entradas
        except Exception:
            pass
    return resultados
