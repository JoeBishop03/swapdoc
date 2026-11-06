"""Every public page on SwapDoc, in one place.

Adding a page here gives it a route, a sitemap entry and its title and
description tags. Guides also need a template in templates/guides/<slug>.html.
"""

UPDATED = "2026-10-25"

PAGES = {
    "/": {
        "template": "index.html",
        "title": "Free Document Converter: Word to PDF & PDF to Word | SwapDoc",
        "description": "Free online document converter: turn Word into PDF or PDF into "
                       "an editable Word doc. No sign-up, no watermark, and files are "
                       "deleted after download.",
        "updated": "2026-10-31",
    },
    "/word-to-pdf": {
        "template": "word_to_pdf.html",
        "title": "Word to PDF Converter: Free, No Sign-up | SwapDoc",
        "description": "Turn a Word document (.docx or .doc) into a PDF in seconds. "
                       "Free, no account, no watermark, and your file is deleted "
                       "after download.",
        "updated": UPDATED,
    },
    "/pdf-to-word": {
        "template": "pdf_to_word.html",
        "title": "PDF to Word Converter: Free & Editable | SwapDoc",
        "description": "Convert a PDF into an editable Word document (.docx) for free. "
                       "No sign-up or watermark, and files are deleted after download.",
        "updated": UPDATED,
    },
    "/doc-to-docx": {
        "template": "doc_to_docx.html",
        "title": "DOC to DOCX Converter (and DOCX to DOC): Free | SwapDoc",
        "description": "Convert old .doc Word files to .docx, or .docx back to .doc, free "
                       "online. No sign-up or watermark; files deleted after download.",
        "updated": "2026-11-06",
    },
    "/guides": {
        "template": "guides_index.html",
        "title": "Guides to Word and PDF Files | SwapDoc",
        "description": "Plain-English guides to converting, editing and sharing Word "
                       "and PDF documents, including how to keep your formatting intact.",
        "updated": UPDATED,
    },
    "/about": {
        "template": "about.html",
        "title": "About SwapDoc",
        "description": "Who runs SwapDoc, how the free Word and PDF converter works, "
                       "and how it stays free.",
        "updated": UPDATED,
    },
    "/contact": {
        "template": "contact.html",
        "title": "Contact SwapDoc",
        "description": "Get in touch with SwapDoc about the converter, a problem file, "
                       "privacy or advertising.",
        "updated": UPDATED,
    },
    "/privacy": {
        "template": "privacy.html",
        "title": "Privacy Policy | SwapDoc",
        "description": "How SwapDoc handles your files and data: what is processed, "
                       "what is deleted, cookies, advertising and visitor statistics.",
        "updated": UPDATED,
    },
    "/terms": {
        "template": "terms.html",
        "title": "Terms of Use | SwapDoc",
        "description": "The terms for using SwapDoc's free document converter.",
        "updated": UPDATED,
    },
}

GUIDES = [
    {
        "slug": "convert-word-to-pdf",
        "title": "How to Convert Word to PDF: 4 Free Ways",
        "short": "How to convert Word to PDF",
        "description": "Four free ways to turn a Word document into a PDF, on Windows, "
                       "Mac, phone or online, plus checks to make before you send it.",
        "summary": "Online, in Word itself, in Google Docs, or with Print to PDF, and "
                   "which to pick.",
        "published": "2026-10-25",
        "updated": UPDATED,
        "minutes": 5,
    },
    {
        "slug": "convert-pdf-to-word",
        "title": "How to Turn a PDF into an Editable Word Document",
        "short": "How to edit a PDF in Word",
        "description": "Three free ways to convert a PDF into an editable Word file, what "
                       "to expect from the layout, and what to do with scanned PDFs.",
        "summary": "Using SwapDoc, Word's own PDF opening, or Google Docs for scanned "
                   "pages.",
        "published": "2026-10-25",
        "updated": UPDATED,
        "minutes": 5,
    },
    {
        "slug": "fix-formatting-after-converting",
        "title": "Why Formatting Changes When You Convert, and How to Fix It",
        "short": "Fixing formatting after converting",
        "description": "Fonts swapped, tables shifted, text boxes everywhere? The common "
                       "causes of layout problems after converting, and how to fix each.",
        "summary": "Fonts, tables, text boxes, columns and page breaks: causes and fixes.",
        "published": "2026-10-25",
        "updated": UPDATED,
        "minutes": 6,
    },
    {
        "slug": "pdf-vs-word",
        "title": "PDF or Word: Which Format Should You Use?",
        "short": "PDF or Word: which to use",
        "description": "When to send a PDF and when to send a Word document, for CVs, "
                       "forms, contracts, invoices and shared drafts.",
        "summary": "A quick rule of thumb, with examples for CVs, contracts and forms.",
        "published": "2026-10-25",
        "updated": UPDATED,
        "minutes": 4,
    },
    {
        "slug": "doc-vs-docx",
        "title": "DOC vs DOCX: What's the Difference?",
        "short": "DOC vs DOCX explained",
        "description": "DOC vs DOCX compared: file size, compatibility, macros and safety, "
                       "how to tell which you have, and how to convert .doc to .docx.",
        "summary": "Side-by-side comparison, which to use, and how to convert between them.",
        "published": "2026-10-25",
        "updated": "2026-11-06",
        "minutes": 6,
    },
    {
        "slug": "google-docs-vs-docx",
        "title": "Google Docs vs DOCX: What's the Difference?",
        "short": "Google Docs vs DOCX",
        "description": "Is a Google Doc the same as a Word file? How Google Docs and .docx "
                       "differ, how to convert between them, and what changes when you do.",
        "summary": "Online document or Word file: when to use each, and how to switch "
                   "without losing formatting.",
        "published": "2026-11-07",
        "updated": "2026-11-07",
        "release": "2026-11-07T08:00:00+00:00",   # 8am UK time (GMT in November)
        "minutes": 6,
    },
]

from datetime import date as _date, datetime as _datetime, timezone as _tz

for _g in GUIDES:
    _g["template"] = f"guides/{_g['slug']}.html"
    _g.setdefault("title_tag", f"{_g['title']} | SwapDoc")
    _d = _date.fromisoformat(_g["updated"])
    _g["updated_label"] = f"{_d.day} {_d:%B %Y}"
    # Scheduled publishing: a guide with "release" (ISO date-time with timezone)
    # stays hidden everywhere (its page, menus, lists, sitemap) until that moment.
    _g["release_at"] = _datetime.fromisoformat(_g["release"]) if _g.get("release") else None

GUIDE_BY_SLUG = {g["slug"]: g for g in GUIDES}


def is_live(guide, now=None):
    now = now or _datetime.now(_tz.utc)
    return guide["release_at"] is None or now >= guide["release_at"]


def live_guides(now=None):
    """Guides visitors and search engines can see right now, newest first."""
    live = [g for g in GUIDES if is_live(g, now)]
    return sorted(live, key=lambda g: g["published"], reverse=True)
