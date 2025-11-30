# -*- coding: utf-8 -*-
"""
Internacional (Alemanha) via Google News RSS — Sustentabilidade e Mudanças Climáticas
- Janela: 14 dias (padrão)
- Foco: Alemanha (DAAD, DFG, Humboldt, BMBF, órgãos ambientais)
- Temas: sustentabilidade, desenvolvimento sustentável, transição energética, mudanças climáticas
- Envia para EMAIL_TO_EXTERIOR

Requer secrets:
- GMAIL_USER
- GMAIL_APP_PASS
- EMAIL_TO_EXTERIOR
"""

import os
import datetime
from urllib.parse import quote_plus
import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ===== Parâmetros (podem ser sobrepostos no workflow) =====
DAYS = int(os.getenv("DAYS_INT", "14"))
MAX_PER_TERM = int(os.getenv("MAX_PER_TERM_INT", "8"))

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASS = os.environ["GMAIL_APP_PASS"]
EMAIL_TO = os.environ["EMAIL_TO_EXTERIOR"]
EMAIL_SUBJECT = os.getenv(
    "EMAIL_SUBJECT_INT",
    f"📨 Editais Alemanha – Sustentabilidade e Mudanças Climáticas (últimos {DAYS} dias)"
)

# Idioma/país para a busca em paralelo:
# EN/US para notícias globais, DE/DE para fontes alemãs, PT/BR para notícias em português sobre Alemanha.
LANG_COUNTRY_PAIRS = [
    ("en", "US"),
    ("de", "DE"),
    ("pt", "BR"),
]

# ===== Termos – Alemanha + sustentabilidade/mudanças climáticas =====
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

    # BMBF e órgãos alemães – clima e sustentabilidade
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

    # Chamadas em português mencionando Alemanha e clima/sustentabilidade
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
      body { font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #222; }
      h2 { margin: 0 0 8px 0; }
      .termo { font-weight: 600; margin-top: 14px; }
      table { border-collapse: collapse; width: 100%; margin-top: 6px; }
      th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
      th { background: #f5f5f5; text-align: left; }
      .muted { color: #666; }
      .nores { color: #a00; }
      .pill { font-size: 12px; color: #555; background:#f0f0f0; padding:2px 6px; border-radius:10px; }
    </style>
    """
    head = (
        f"<h2>Editais Alemanha – Sustentabilidade e Mudanças Climáticas (últimos {dias} dias)</h2>"
        f"<p class='muted'>Fonte: Google News RSS • Foco em Alemanha (DAAD, DFG, Humboldt, BMBF e órgãos ambientais) "
        f"com chamadas ligadas a sustentabilidade, transição energética e mudanças climáticas. "
        f"Idiomas: EN, DE e PT.</p>"
    )

    blocks = []
    for termo, itens in noticias.items():
        if not itens:
            blocks.append(
                f"<div class='termo'>🔎 {termo}</div>"
                f"<div class='nores'>⚠️ Sem resultados</div>"
            )
        else:
            linhas = "".join(
                f"<tr>"
                f"<td>{i['data']}</td>"
                f"<td><a href='{i['link']}' target='_blank' rel='noopener noreferrer'>{i['titulo']}</a><br>"
                f"<span class='pill'>{i['lang'].upper()}-{i['country'].upper()}</span></td>"
                f"</tr>"
                for i in itens
            )
            blocks.append(
                f"<div class='termo'>🔎 {termo}</div>"
                f"<table><thead><tr><th>Data</th><th>Título / Link</th></tr></thead>"
                f"<tbody>{linhas}</tbody></table>"
            )

    return f"<!DOCTYPE html><html><head>{style}</head><body>{head}{''.join(blocks)}</body></html>"


def txt_email(noticias, dias):
    out = [f"Editais Alemanha – Sustentabilidade e Mudanças Climáticas (últimos {dias} dias)", ""]
    for termo, itens in noticias.items():
        out.append(f"🔎 {termo}")
        if not itens:
            out.append("  - Sem resultados")
        else:
            for i in itens[:5]:
                out.append(
                    f"  - [{i['data']}] {i['titulo']} ({i['lang'].upper()}-{i['country'].upper()})  {i['link']}"
                )
        out.append("")
    return "\n".join(out)


def enviar(corpo_txt, corpo_html):
    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = EMAIL_SUBJECT
    msg.attach(MIMEText(corpo_txt, "plain", "utf-8"))
    msg.attach(MIMEText(corpo_html, "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=45) as s:
        s.starttls()
        s.login(GMAIL_USER, GMAIL_APP_PASS)
        s.send_message(msg)


def main():
    data = buscar_multilingue(TERMS, LANG_COUNTRY_PAIRS, DAYS, MAX_PER_TERM)
    enviar(txt_email(data, DAYS), html_email(data, DAYS))
    total = sum(len(v) for v in data.values())
    print(f"INT-ALEMANHA SUSTENTABILIDADE/CLIMA OK: {total} itens enviados para {EMAIL_TO}")


if __name__ == "__main__":
    main()
