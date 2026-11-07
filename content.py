"""Every public page on SwapDoc, in one place.

Adding a page here gives it a route, a sitemap entry and its title and
description tags. Guides also need a template in templates/guides/<slug>.html.
"""

UPDATED = "2026-10-25"

# Shown as the byline on every guide and on the About page.
AUTHOR = {
    "name": "Joe Bishop",
    "url": "/about#who",
    "bio": "Joe built and runs SwapDoc from the UK and writes its guides. SwapDoc's "
           "converters are tested on real documents, and the results are published on "
           "each converter page.",
}

# When the converter pages' test results were last re-run.
TESTED = "2026-11-07"
TESTED_LABEL = "7 November 2026"

PAGES = {
    "/": {
        "template": "index.html",
        "title": "Free Document Converter: Word to PDF & PDF to Word | SwapDoc",
        "description": "Free online document converter: turn Word into PDF or PDF into "
                       "an editable Word doc. No sign-up, no watermark, and files are "
                       "deleted after download.",
        "updated": "2026-11-07",
    },
    "/word-to-pdf": {
        "template": "word_to_pdf.html",
        "title": "Word to PDF Converter: Free, No Sign-up | SwapDoc",
        "description": "Turn a Word document (.docx or .doc) into a PDF in seconds. "
                       "Free, no account, no watermark, and your file is deleted "
                       "after download.",
        "updated": "2026-11-07",
    },
    "/pdf-to-word": {
        "template": "pdf_to_word.html",
        "title": "PDF to Word Converter: Free & Editable | SwapDoc",
        "description": "Convert a PDF into an editable Word document (.docx) for free. "
                       "No sign-up or watermark, and files are deleted after download.",
        "updated": "2026-11-07",
    },
    "/doc-to-docx": {
        "template": "doc_to_docx.html",
        "title": "DOC to DOCX Converter (and DOCX to DOC): Free | SwapDoc",
        "description": "Convert old .doc Word files to .docx, or .docx back to .doc, free "
                       "online. No sign-up or watermark; files deleted after download.",
        "updated": "2026-11-07",
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
        "updated": "2026-11-07",
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
    # --- November 2026 batch: 2 live at once, then Tuesdays and Fridays at 8am UK time ---
    {
        "slug": "why-fonts-change-in-pdf",
        "title": "Why Your Font Changed When You Converted to PDF",
        "short": "Why fonts change in a PDF",
        "description": "Why a PDF can come out in a different font from your Word document, "
                       "which fonts are safe, and four ways to keep your exact font.",
        "summary": "Which fonts convert exactly, which get swapped, and how to keep yours.",
        "published": "2026-11-07",
        "updated": "2026-11-07",
        "minutes": 6,
    },
    {
        "slug": "remove-tracked-changes-before-pdf",
        "title": "How to Remove Tracked Changes and Comments Before Making a PDF",
        "title_tag": "Remove Tracked Changes and Comments Before a PDF | SwapDoc",
        "short": "Removing tracked changes and comments",
        "description": "Stop tracked changes and comments ending up in your PDF or shared "
                       "file. Steps for Word on Windows and Mac, Google Docs and LibreOffice.",
        "summary": "Accept changes, delete comments and clear hidden details before sharing.",
        "published": "2026-11-07",
        "updated": "2026-11-07",
        "minutes": 5,
    },
    {
        "slug": "aptos-vs-calibri",
        "title": "Aptos vs Calibri: Word's New Default Font Explained",
        "short": "Aptos vs Calibri",
        "description": "Why Word switched from Calibri to Aptos, how the two fonts differ, "
                       "what happens when you share an Aptos document, and how to switch back.",
        "summary": "What changed, why it matters when you share files, and how to switch back.",
        "published": "2026-11-10",
        "updated": "2026-11-10",
        "release": "2026-11-10T08:00:00+00:00",
        "minutes": 5,
    },
    {
        "slug": "scanned-pdf-to-text",
        "title": "How to Turn a Scanned PDF into Editable Text for Free",
        "short": "Scanned PDF to editable text",
        "description": "How to tell if a PDF is scanned, and five free ways to get editable "
                       "text from it with OCR on Windows, Mac, iPhone, Android and online.",
        "summary": "Free OCR with Google Docs, OneNote, Mac Preview and your phone.",
        "published": "2026-11-13",
        "updated": "2026-11-13",
        "release": "2026-11-13T08:00:00+00:00",
        "minutes": 6,
    },
    {
        "slug": "cv-pdf-or-word",
        "title": "Should You Send Your CV as a PDF or Word Document?",
        "short": "CV: PDF or Word?",
        "description": "When to send your CV as a PDF and when to send Word, what applicant "
                       "tracking systems can read, and checks before you hit send.",
        "summary": "The UK rule of thumb, what recruiters and tracking systems need, and checks.",
        "published": "2026-11-17",
        "updated": "2026-11-17",
        "release": "2026-11-17T08:00:00+00:00",
        "minutes": 5,
    },
    {
        "slug": "reduce-pdf-file-size",
        "title": "How to Reduce a PDF's File Size for Email or Upload",
        "short": "Making a PDF smaller",
        "description": "Why PDFs get big and how to make them smaller for free, on Windows "
                       "and Mac, without making the text blurry.",
        "summary": "Shrink the pictures, re-export from Word, or compress on a Mac.",
        "published": "2026-11-20",
        "updated": "2026-11-20",
        "release": "2026-11-20T08:00:00+00:00",
        "minutes": 5,
    },
    {
        "slug": "reduce-word-file-size",
        "title": "How to Make a Word Document Smaller",
        "short": "Making a Word file smaller",
        "description": "Find out what's making your Word document big and shrink it: "
                       "compress pictures, drop embedded fonts and objects, and save as .docx.",
        "summary": "Find what's taking the space, then shrink pictures, fonts and objects.",
        "published": "2026-11-24",
        "updated": "2026-11-24",
        "release": "2026-11-24T08:00:00+00:00",
        "minutes": 5,
    },
    {
        "slug": "open-docx-without-word",
        "title": "How to Open a DOCX File Without Microsoft Word",
        "short": "Opening DOCX without Word",
        "description": "Six free ways to open, edit or print a .docx file without buying "
                       "Microsoft Word, on Windows, Mac, Chromebook and phone.",
        "summary": "Free options on every device, and which keeps formatting best.",
        "published": "2026-11-27",
        "updated": "2026-11-27",
        "release": "2026-11-27T08:00:00+00:00",
        "minutes": 5,
    },
    {
        "slug": "sign-a-pdf",
        "title": "How to Sign a PDF for Free (Windows, Mac and Phone)",
        "short": "Signing a PDF for free",
        "description": "Add your signature to a PDF for free with Adobe Reader, Mac Preview, "
                       "an iPhone or Android, plus when an electronic signature is enough.",
        "summary": "Free ways to sign on any device, and when e-signatures are valid.",
        "published": "2026-12-01",
        "updated": "2026-12-01",
        "release": "2026-12-01T08:00:00+00:00",
        "minutes": 5,
    },
    {
        "slug": "password-protect-documents",
        "title": "How to Password-Protect a Word Document or PDF",
        "short": "Password-protecting documents",
        "description": "Add a password to a Word document or PDF on Windows or Mac, the "
                       "difference between locking and restricting editing, and safe sharing.",
        "summary": "Proper encryption in Word, PDF and LibreOffice, and sharing the password.",
        "published": "2026-12-04",
        "updated": "2026-12-04",
        "release": "2026-12-04T08:00:00+00:00",
        "minutes": 5,
    },
    {
        "slug": "merge-pdf-files",
        "title": "How to Merge PDF Files for Free",
        "short": "Merging PDF files",
        "description": "Combine several PDFs into one for free: built-in tools on Mac and "
                       "iPhone, free apps for Windows, and merging Word files before converting.",
        "summary": "Built-in tools on Mac and iPhone, free apps for Windows, and a Word trick.",
        "published": "2026-12-08",
        "updated": "2026-12-08",
        "release": "2026-12-08T08:00:00+00:00",
        "minutes": 5,
    },
    {
        "slug": "accessible-pdf-from-word",
        "title": "How to Make an Accessible PDF from a Word Document",
        "short": "Making an accessible PDF",
        "description": "Make a PDF that works with screen readers: headings, alt text, "
                       "tables, links and the right way to save, with a checklist.",
        "summary": "Seven fixes in Word, then save it the right way. Includes a checklist.",
        "published": "2026-12-11",
        "updated": "2026-12-11",
        "release": "2026-12-11T08:00:00+00:00",
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
