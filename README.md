# SwapDoc

Free online document converter at **[www.swapdoc.co.uk](https://www.swapdoc.co.uk)**: Word to PDF, PDF to Word, and DOC ⇄ DOCX. No sign-up, no watermark, and files are deleted as soon as they're downloaded.

Built with Flask, with conversions done by LibreOffice (headless) in a Docker container on Azure Container Apps.

## What's where

| Path | What it is |
|---|---|
| `app.py` | The web app: conversion endpoint, page routes, redirects, security headers, `sitemap.xml`, `robots.txt`, `ads.txt` |
| `content.py` | Every page and guide, with titles, descriptions and dates. Guides can be scheduled with a `release` time |
| `templates/` | Page templates. `base.html` is shared by all pages; `guides/` holds the articles |
| `static/` | Stylesheet (inlined into pages at start-up), scripts, self-hosted fonts and icons |
| `infra/` | Azure template for Application Insights and the "SwapDoc visitors" dashboard (`build_template.py` generates `analytics.json`) |
| `deploy/deploy.ps1` | One-command deploy to Azure |
| `docs/SETUP-GUIDE.md` | Domain, deployment, dashboard, Search Console and AdSense guide |
| `brand/` | Logos |
| `.github/workflows/` | Builds the Docker image into Azure Container Registry on every push to `main` (doesn't change the live site) |

## Run it locally

```powershell
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\python -m flask --app app run --port 8000
```

Pages work locally. Conversions need LibreOffice (`soffice`) on the PATH, as in the Docker image.

## Deploy

```powershell
az login --use-device-code --tenant <tenant-id>
.\deploy\deploy.ps1 -ResourceGroup swapdoc-rg -SkipAnalytics
```

This builds the image in Azure and switches the Container App to it. Leave out `-SkipAnalytics` to also (re)create Application Insights and the dashboard. See [docs/SETUP-GUIDE.md](docs/SETUP-GUIDE.md).

## Adding a guide

1. Write `templates/guides/<slug>.html` (copy an existing guide).
2. Add it to `GUIDES` in `content.py`. Add `"release": "2026-12-01T08:00:00+00:00"` to publish it automatically at that time.
3. Deploy. The menu, guide list and sitemap update by themselves.

## Privacy

Uploaded files are deleted after download. Visitor statistics are cookie-free (anonymous daily ID; no IP addresses stored). See the [privacy policy](https://www.swapdoc.co.uk/privacy).
