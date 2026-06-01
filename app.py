import os
import uuid
import time
import threading
import subprocess
from flask import Flask, request, render_template, send_file, jsonify, after_this_request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/tmp/outputs")
MAX_AGE_SECONDS = 600          # files older than this get swept regardless
MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB upload cap

# How many conversions one visitor may do. Adjust freely (env-overridable).
# Two limits apply together: a short burst cap and an hourly cap.
RATE_LIMITS = os.environ.get("RATE_LIMITS", "5 per minute;30 per hour")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def client_ip():
    """Real visitor IP. Behind Azure Container Apps' ingress the original
    client address is in X-Forwarded-For (first entry); remote_addr would
    otherwise be the proxy, lumping all users together."""
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return get_remote_address()


limiter = Limiter(
    key_func=client_ip,
    app=app,
    default_limits=[],          # only the endpoints we mark are limited
    storage_uri="memory://",    # per-replica counts; see note in deploy guide
)


@app.errorhandler(429)
def ratelimit_handler(e):
    # Frontend reads .error from JSON, so return JSON it can display.
    return jsonify(error="You've reached the conversion limit. "
                         "Please wait a little and try again."), 429

ALLOWED = {
    "docx": "pdf",
    "doc": "pdf",
    "pdf": "docx",
}


def soffice_convert(src_path, target_ext, out_dir):
    """Convert using LibreOffice headless. Returns output file path."""
    src_ext = os.path.splitext(src_path)[1].lower().lstrip(".")

    if src_ext == "pdf" and target_ext == "docx":
        # PDF must be imported via the Writer PDF filter, with an explicit
        # output filter, otherwise LibreOffice reports "no export filter".
        cmd = ["soffice", "--headless",
               "--infilter=writer_pdf_import",
               "--convert-to", "docx:MS Word 2007 XML",
               "--outdir", out_dir, src_path]
    else:
        cmd = ["soffice", "--headless", "--convert-to", target_ext,
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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


SITE = "https://www.swapdoc.co.uk"


@app.route("/robots.txt")
def robots():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE}/sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    pages = ["/", "/privacy"]
    urls = "".join(
        f"<url><loc>{SITE}{p}</loc><changefreq>monthly</changefreq></url>"
        for p in pages
    )
    body = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'{urls}</urlset>')
    return Response(body, mimetype="application/xml")


@app.route("/healthz")
def healthz():
    return "ok", 200


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

    target = ALLOWED[ext]
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
