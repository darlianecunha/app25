# -*- coding: utf-8 -*-
"""
EXTERIOR2 Alemanha - Sustentabilidade e Mudanças Climáticas

Chamadas e bolsas ligadas à Alemanha (DAAD, DFG, Humboldt, BMBF etc.)
com foco em pesquisa em sustentabilidade e mudanças climáticas.

Idiomas: EN/DE/PT (pesquisas paralelas)
Janela padrão: 14 dias
Envia para: EMAIL_TO_EXTERIOR2

Secrets necessários:
- GMAIL_USER
- GMAIL_APP_PASS
- EMAIL_TO_EXTERIOR2
"""

import os
import datetime
from urllib.parse import quote_plus
import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ===== Parâmetros sobreponíveis por ENV =====
DAYS = int(os.getenv("DAYS_EXT2", "14"))
MAX_PER_TERM = int(os.getenv("MAX_PER_TERM_EXT2", "8"))
EMAIL_SUBJECT = os.getenv(
    "EMAIL_SUBJECT_EXT2",
    f"📨 Editais Alemanha - Sustentabilidade e Mudanças Climáticas (últimos {DAYS} dias)"
)

# Conjuntos de idioma/país (formato: [(lang, country)])
# EN/US para notícias globais, DE/DE para fontes alemãs,
# PT/BR para notícias em português sobre Alemanha.
LANG_COUNTRY_PAIRS = [
    ("en", "US"),
    ("de", "DE"),
    ("pt", "BR"),
]

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASS = os.environ["GMAIL_APP_PASS"]
EMAIL_TO = os.environ["EMAIL_TO_EXTERIOR2"]

# ===== Termos - Alemanha + sustentabilidade/mudanças climáticas =====
TERMS = [
    # DAAD – sustentabilidade e clima
    'site:daad.de "climate change" research',
    'site:daad.de "climate change" scholarship',
    'site:daad.de "sustainable development" research',
    'site:daad.de sustainability scholarship',
    'site:daad.de Nachhaltigkeit Forschung',
    'site:daad.de Klimawandel Forschung',
    'site:daad.de "climate action" research funding',

    # DFG – sustentabilidade e clima
    'site:dfg.de "climate change" research funding',
    'site:dfg.de Klimawandel Forschungsförderung',
    'site:dfg.de Nachhaltigkeit Schwerpunktprogramm',
    'site:dfg.de "sustainability" research project',
    'site:dfg.de "climate and energy" call for proposals',

    # Humboldt Foundation – sustentabilidade e clima
    'site:humboldt-foundation.de "climate change" fellowship',
    'site:humboldt-foundation.de climate and sustainability research',
    'site:humboldt-foundation.de "sustainable development" research',
    'site:avh.de Klimawandel Stipendium',
    'site:avh.de Nachhaltigkeit Forschung',

    # BMBF e ministérios alemães – clima e sustentabilidade
    'site:bmbf.de "climate change" research funding',
    'site:bmbf.de Klimawandel Förderaufruf',
    'site:bmbf.de Nachhaltigkeit Forschungsförderung',
    'site:bmbf.de "sustainable development" research',
    'site:umweltbundesamt.de Klimawandel Forschung',
    'site:umweltbundesamt.de Nachhaltigkeit Forschungsprojekt',

    # Chamadas em inglês com foco em Alemanha, clima e sustentabilidade
    'Germany "climate change" research funding call',
    'Germany "sustainability" research grant',
    'Germany "sustainable development" postdoctoral fellowship',

    # Chamadas em português que mencionem Alemanha e clima/sustentabilidade
    'Alemanha "mudanças climáticas" bolsa de pesquisa',
    'Alemanha sustentabilidade edital pesquisa',
    'Alemanha "transição energética" oportunidades de pesquisa',

    # Cooperação Brasil–Alemanha em clima/sustentabilidade
    'Brazil Germany "climate change" research programme',
    'Brazil Germany sustainability research call',
    'Brasil Alemanha "mudanças climáticas" cooperação científica',
]


def buscar_multilingue(termos, pairs, dias, max_per_termo):
    """
    Faz busca em vários idiomas/países e consolida resultados por termo,
    removendo duplicados (mesmo link ou mesmo título).
    """
    hoje = datetime.date.today()
    limite = hoje - datetime.timedelta(days=dias)
    resultados = {}

    for termo in termos:
        vistos_por_link = set()
        vistos_por_titulo = set()
        itens = []

        for lang, country in pairs:
            q = quote_plus(termo)
            url = (
                f"https://news.google.com/rss/search?"
                f"q={q}&hl={lang}&gl={country}&ceid={country}:{lang}"
            )
            feed = feedparser.parse(url)

            for e in feed.entries:
                dp = e.get("published_parsed")
                if not dp:
                    continue
                d = datetime.date(*dp[:3])
                if d < limite:
                    continue

                title = (e.title or "").strip()
                link = (e.link or "").strip()

                if not title or not link:
                    continue

                key_link = link.lower()
                key_title = title.lower()

                if key_link in vistos_por_link or key_title in vistos_por_titulo:
                    continue

                vistos_por_link.add(key_link)
                vistos_por_titulo.add(key_title)

                itens.append({
                    "data": d.strftime("%d/%m/%Y"),
                    "titulo": title,
                    "link": link,
                    "lang": lang,
                    "country": country,
                })

        itens = sorted(
            itens,
            key=lambda x: datetime.datetime.strptime(x["data"], "%d/%m/%Y"),
            reverse=True
        )[:max_per_termo]

        resultados[termo] = itens

    return resultados


def html_email(noticias, dias):
    style = """
    <style>
      body { font-family: Arial, Helvetica, sans-serif; font-si
