import os

# --- Azure Application Insights (server side) -------------------------------
# Switched on only when the connection string is set on the Container App.
# It must run before Flask is imported so that requests are traced.
if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor()
    except Exception as exc:  # never let monitoring stop the site starting
        print(f"Application Insights not started: {exc}")

import hashlib
import hmac
import secrets
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone

from flask import (Flask, Response, abort, after_this_request, g, jsonify,
                   redirect, render_template, request, send_file,
                   send_from_directory)
from flask_compress import Compress
from flask_limiter import Limiter
from werkzeug.middleware.proxy_fix import ProxyFix

import content

app = Flask(__name__)
# Azure Container Apps sits in front of the app and passes the visitor's real
# address in X-Forwarded-For. ProxyFix makes request.remote_addr that address,
# for rate limits, visitor counts and server-side location data.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/tmp/outputs")
MAX_AGE_SECONDS = 600          # files older than this get swept regardless
MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB upload cap

# How many conversions one visitor may do. Adjust freely (env-overridable).
# Two limits apply together: a short burst cap and an hourly cap.
RATE_LIMITS = os.environ.get("RATE_LIMITS", "5 per minute;30 per hour")

SITE = os.environ.get("SITE_URL", "https://www.swapdoc.co.uk").rstrip("/")
CANONICAL_HOST = SITE.split("://", 1)[1]
APEX_HOST = CANONICAL_HOST.removeprefix("www.")

# Google AdSense. Ad slot IDs come from AdSense > Ads > By ad unit. While they
# are empty no fixed ad boxes are drawn; Auto ads (switched on in AdSense)
# still place ads automatically.
ADSENSE_CLIENT = os.environ.get("ADSENSE_CLIENT", "ca-pub-5734256894506579")
AD_SLOT_TOP = os.environ.get("AD_SLOT_TOP", "")
AD_SLOT_CONTENT = os.environ.get("AD_SLOT_CONTENT", "")

# Visitor analytics (browser side). Empty = no tracking script on the page.
AI_CONNECTION_STRING = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
# Key for the anonymous daily visitor ID. Set it on the Container App so all
# replicas agree; a random fallback still works with a single replica.
VISITOR_SALT = os.environ.get("VISITOR_SALT") or secrets.token_hex(32)

# Bump when CSS/JS change: their URLs carry ?v=, so browsers can cache them for a year.
STATIC_VERSION = "20261106"

# The stylesheet is small (about 3 KB compressed), so it's built into every page
# instead of being a separate file the browser has to wait for before drawing.
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "css", "site.css"),
          encoding="utf-8") as _css:
    INLINE_CSS = _css.read()

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60 * 60 * 24 * 365  # static files: 1 year

# Compress pages, CSS and JS (gzip/brotli), roughly 60-70% smaller. Converted
# documents aren't touched: PDF and Word files aren't in the list of types.
app.config["COMPRESS_MIMETYPES"] = [
    "text/html", "text/css", "text/plain", "text/xml", "application/xml",
    "application/javascript", "text/javascript", "application/json", "image/svg+xml",
]
app.config["COMPRESS_ALGORITHM"] = ["br", "gzip"]
Compress(app)


limiter = Limiter(
    key_func=lambda: request.remote_addr or "unknown",
    app=app,
    default_limits=[],          # only the endpoints we mark are limited
    storage_uri="memory://",    # per-replica counts
)


# --- Hosts, redirects and headers -------------------------------------------

@app.before_request
def canonical_host():
    host = (request.host or "").split(":")[0].lower()
    # swapdoc.co.uk (no www) -> https://www.swapdoc.co.uk, keeping the path.
    if host == APEX_HOST:
        target = SITE + request.full_path.rstrip("?")
        return redirect(target, code=301)
    # One address per page: /guides/ and /Word-To-PDF go to /guides and /word-to-pdf.
    path = request.path
    if request.method in ("GET", "HEAD") and not path.startswith("/static/"):
        clean = path.rstrip("/").lower() or "/"
        if clean != path:
            qs = request.query_string.decode()
            return redirect(clean + (f"?{qs}" if qs else ""), code=301)
    return None


def csp_nonce():
    """A random value per page. Only <script> tags carrying it may run (see CSP below)."""
    if "csp_nonce" not in g:
        g.csp_nonce = secrets.token_urlsafe(16)
    return g.csp_nonce


@app.after_request
def headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    if resp.mimetype == "text/html":
        # Google's recommended "strict CSP": scripts run only if they carry this
        # page's nonce, or were loaded by one that does ('strict-dynamic'). That's
        # how AdSense loads its own scripts. https: and 'unsafe-inline' are only
        # fallbacks for very old browsers; modern ones ignore them.
        resp.headers["Content-Security-Policy"] = (
            f"script-src 'nonce-{csp_nonce()}' 'strict-dynamic' https: 'unsafe-inline'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'self'"
        )
        # Isolates the page from other windows, but still lets ad clicks open tabs.
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    host = (request.host or "").split(":")[0].lower()
    if host in (CANONICAL_HOST, APEX_HOST):
        resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    elif host.endswith(".azurecontainerapps.io"):
        # The Azure test address shouldn't compete with the real domain in Google.
        resp.headers["X-Robots-Tag"] = "noindex"
    return resp


def visitor_id():
    """Anonymous ID that changes every day (UTC). Made from the visitor's IP and
    browser with a secret key, so the IP itself is never sent or stored, and
    nothing is saved on the visitor's device (no cookie needed)."""
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw = f"{day}|{request.remote_addr}|{request.headers.get('User-Agent', '')}"
    return hmac.new(VISITOR_SALT.encode(), raw.encode(), hashlib.sha256).hexdigest()[:24]


@app.context_processor
def site_globals():
    return {
        "SITE": SITE,
        "ADSENSE_CLIENT": ADSENSE_CLIENT,
        "AD_SLOT_TOP": AD_SLOT_TOP,
        "AD_SLOT_CONTENT": AD_SLOT_CONTENT,
        "AI_CONNECTION_STRING": AI_CONNECTION_STRING,
        "visitor_id": visitor_id,
        "v": STATIC_VERSION,
        "csp_nonce": csp_nonce,
        "INLINE_CSS": INLINE_CSS,
        "year": datetime.now(timezone.utc).year,
        "nav_guides": content.live_guides(),
        # For linking to a scheduled guide only once it's out (no broken links before).
        "guide_live": lambda slug: slug in content.GUIDE_BY_SLUG
                                   and content.is_live(content.GUIDE_BY_SLUG[slug]),
    }


# --- Conversion -------------------------------------------------------------

@app.errorhandler(429)
def ratelimit_handler(e):
    # Frontend reads .error from JSON, so return JSON it can display.
    return jsonify(error="You've reached the conversion limit. "
                         "Please wait a little and try again."), 429


@app.errorhandler(413)
def too_large(e):
    return jsonify(error="That file is over the 25 MB limit."), 413


# What each upload turns into when the page doesn't ask for anything else.
ALLOWED = {
    "docx": "pdf",
    "doc": "pdf",
    "pdf": "docx",
}
# Every (from, to) pair the converter supports. Pages can ask for a target
# (the DOC <-> DOCX page sends target=doc or target=docx).
CONVERSIONS = {
    ("docx", "pdf"), ("doc", "pdf"), ("pdf", "docx"),
    ("doc", "docx"), ("docx", "doc"),
}
# LibreOffice export filters, named explicitly so the right Word format is written.
EXPORT_FILTER = {
    "pdf": "pdf",
    "docx": "docx:MS Word 2007 XML",
    "doc": "doc:MS Word 97",
}


def soffice_convert(src_path, target_ext, out_dir):
    """Convert using LibreOffice headless. Returns output file path."""
    src_ext = os.path.splitext(src_path)[1].lower().lstrip(".")

    if src_ext == "pdf" and target_ext == "docx":
        # PDF must be imported via the Writer PDF filter, with an explicit
        # output filter, otherwise LibreOffice reports "no export filter".
        cmd = ["soffice", "--headless",
               "--infilter=writer_pdf_import",
               "--convert-to", EXPORT_FILTER["docx"],
               "--outdir", out_dir, src_path]
    else:
        cmd = ["soffice", "--headless", "--convert-to", EXPORT_FILTER[target_ext],
               "--outdir", out_dir, src_path]

    subprocess.run(
        cmd, check=True, timeout=120,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    base = os.path.splitext(os.path.basename(src_path))[0]
    produced = os.path.join(out_dir, f"{base}.{target_ext}")
    if not os.path.exists(produced):
        raise RuntimeError("Conversion produced no output")
    return produced


def safe_remove(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def sweeper():
    """Background thread: delete any file older than MAX_AGE_SECONDS."""
    while True:
        now = time.time()
        for d in (UPLOAD_DIR, OUTPUT_DIR):
            for f in os.listdir(d):
                p = os.path.join(d, f)
                try:
                    if now - os.path.getmtime(p) > MAX_AGE_SECONDS:
                        os.remove(p)
                except OSError:
                    pass
        time.sleep(120)


threading.Thread(target=sweeper, daemon=True).start()


@app.route("/convert", methods=["POST"])
@limiter.limit(RATE_LIMITS)
def convert():
    if "file" not in request.files:
        return jsonify(error="No file uploaded"), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify(error="Empty filename"), 400

    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED:
        return jsonify(error="Only .docx, .doc and .pdf are supported"), 400

    target = (request.form.get("target") or ALLOWED[ext]).lower()
    if (ext, target) not in CONVERSIONS:
        if ext == target:
            return jsonify(error=f"That file is already a .{ext}."), 400
        return jsonify(error=f"Converting .{ext} to .{target} isn't supported on this page."), 400
    token = uuid.uuid4().hex
    src_name = f"{token}.{ext}"
    src_path = os.path.join(UPLOAD_DIR, src_name)
    f.save(src_path)

    out_path = None
    try:
        out_path = soffice_convert(src_path, target, OUTPUT_DIR)
    except subprocess.TimeoutExpired:
        safe_remove(src_path)
        return jsonify(error="Conversion timed out"), 504
    except Exception:
        safe_remove(src_path)
        safe_remove(out_path)
        return jsonify(error="Conversion failed"), 500

    download_name = (f.filename.rsplit(".", 1)[0] or "converted") + f".{target}"

    @after_this_request
    def cleanup(response):
        # Delete both the upload and the generated file once sent.
        safe_remove(src_path)
        safe_remove(out_path)
        return response

    return send_file(out_path, as_attachment=True, download_name=download_name)


# --- Pages ------------------------------------------------------------------

def render_page(path):
    page = content.PAGES[path]
    return render_template(page["template"], page=page, path=path)


def add_page_route(path):
    endpoint = "page_" + (path.strip("/").replace("-", "_").replace("/", "_") or "home")
    app.add_url_rule(path, endpoint, lambda: render_page(path))


for _path in content.PAGES:
    add_page_route(_path)


@app.route("/guides/<slug>")
def guide(slug):
    g = content.GUIDE_BY_SLUG.get(slug)
    if not g or not content.is_live(g):   # unknown, or scheduled for later
        abort(404)
    return render_template(f"guides/{slug}.html", page=g, guide=g,
                           path=f"/guides/{slug}")


@app.errorhandler(404)
def not_found(e):
    page = {"title": "Page not found | SwapDoc", "description": "", "noindex": True}
    return render_template("404.html", page=page, path=request.path), 404


# --- Files search engines and ad networks look for --------------------------

@app.route("/robots.txt")
def robots():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /convert\n"
        f"Sitemap: {SITE}/sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    live = content.live_guides()
    newest_guide = max(g["updated"] for g in live)
    entries = []
    for p, pg in content.PAGES.items():
        if pg.get("noindex"):
            continue
        # The home page and guide list change whenever a guide is published.
        d = max(pg["updated"], newest_guide) if p in ("/", "/guides") else pg["updated"]
        entries.append((p, d))
    entries += [(f"/guides/{g['slug']}", g["updated"]) for g in live]
    urls = "".join(
        f"<url><loc>{SITE}{p}</loc><lastmod>{d}</lastmod></url>"
        for p, d in entries
    )
    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'{urls}</urlset>')
    return Response(body, mimetype="application/xml")


@app.route("/ads.txt")
def ads_txt():
    # Tells ad buyers SwapDoc is allowed to sell its ad space through AdSense.
    if not ADSENSE_CLIENT.startswith("ca-pub-"):
        abort(404)
    pub = ADSENSE_CLIENT.removeprefix("ca-")
    return Response(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n",
                    mimetype="text/plain")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.ico",
                               mimetype="image/x-icon")


@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
