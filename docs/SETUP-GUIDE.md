# SwapDoc: domain, dashboard, SEO and AdSense guide

Last checked: 25 October 2026.

| Part | What it does | Time |
|---|---|---|
| [1. Fix the domain](#1-fix-the-domain) | Makes `swapdoc.co.uk` (without www) open the site | 15 min + DNS wait |
| [2. Deploy the new version](#2-deploy-the-new-version) | Puts the new pages and visitor tracking live, and creates the dashboard | 20 min |
| [3. Use the dashboard](#3-use-the-visitor-dashboard) | Shows who visits, where from, which pages, how long | 2 min |
| [4. Google Search Console and Bing](#4-google-search-console-and-bing) | Gets the new pages into search results | 15 min |
| [5. AdSense](#5-adsense) | Gets the site approved and ads showing legally in the UK | 20 min + Google review |

---

## 1. Fix the domain

**What's wrong:** `www.swapdoc.co.uk` works. `swapdoc.co.uk` (no www) still points at IONOS, which shows a German "Domain ist bereits registriert" parking page. Most people, and Google AdSense, type the domain without www, so the site looks like it's down.

Current DNS, checked 25 October 2026:

| Name | Type | Points to | OK? |
|---|---|---|---|
| `www.swapdoc.co.uk` | CNAME | `swapdoc.icypond-0590a0e8.uksouth.azurecontainerapps.io` | Yes |
| `swapdoc.co.uk` | A | `217.160.0.242` (IONOS parking) | **No** |
| `swapdoc.co.uk` | AAAA | `2001:8d8:100f:f000::200` (IONOS parking) | **No** |
| `swapdoc.co.uk` | MX | Proton Mail | Yes, leave alone |

There are two ways to fix it. **Option A is recommended:** everything stays in Azure, and the new SwapDoc code already redirects `swapdoc.co.uk` to `https://www.swapdoc.co.uk`.

### Option A (recommended): point the bare domain at Azure

**In IONOS** (ionos.co.uk → **Domains & SSL** → `swapdoc.co.uk` → **DNS**):

1. Edit the **A** record for `@` (the bare domain). Change `217.160.0.242` to **`20.108.209.63`** (your Azure Container Apps address).
2. **Delete** the **AAAA** record for `@`. Azure Container Apps doesn't use IPv6, and leaving it would send some visitors to IONOS.
3. **Add** a **TXT** record:
   - Host name: **`asuid`**
   - Value: **`54453C9735E8EFFD90EB7822706D99F072C44207903F4EF44109012F0CA7D2E3`**

   This proves to Azure that you own the domain. It's the same code already on `asuid.www`.
4. Don't touch the `www` CNAME, the MX records, or the TXT records for Proton and Google.

If IONOS asks whether to change the domain's "destination" or "usage", choose the custom DNS/A-record option. Don't choose forwarding or an IONOS website.

**In Azure** (portal.azure.com → **Container Apps** → **swapdoc** → **Settings → Custom domains**), after about 15–60 minutes so the DNS change has spread:

1. **Add custom domain** → **Managed certificate**.
2. Domain: **`swapdoc.co.uk`**. Hostname record type: **A record**.
3. Click **Validate**. If it fails, wait 30 minutes and try again.
4. Click **Add**. The free certificate takes 5–20 minutes to appear as **Secured**.

**Done when:** `https://swapdoc.co.uk/pdf-to-word` jumps to `https://www.swapdoc.co.uk/pdf-to-word`, with a padlock and no warning. The redirect is part of the new code, so do Part 2 first, or at the same time.

### Option B: use IONOS forwarding

Simpler, but it relies on IONOS's free certificate for the HTTPS version.

1. IONOS → **Domains & SSL** → `swapdoc.co.uk` → **Adjust destination** (or the gear icon) → **Forwarding**.
2. Target: **`https://www.swapdoc.co.uk`**. Type: **HTTP redirect (301)**, not frame redirect.
3. If asked, apply it **only to `swapdoc.co.uk`, not `www`**. Afterwards, check `https://www.swapdoc.co.uk` still opens the site.
4. Check `https://swapdoc.co.uk` too. If the browser shows a certificate warning, go to **Domains & SSL → SSL certificates** in IONOS and assign the free SSL certificate to `swapdoc.co.uk`.

---

## 2. Deploy the new version

What's new in this version:

- **New pages:** `/word-to-pdf`, `/pdf-to-word`, five guides under `/guides`, plus `/about`, `/contact` and `/terms`. AdSense rejects one-page tool sites as "low-value content", so these matter.
- **SEO:** a title, description, canonical address, link-preview image, structured data and breadcrumbs on every page; a sitemap listing all 13 pages with dates; a favicon; a proper 404 page.
- **AdSense:** `ads.txt` is generated automatically, and the placeholder ad units (slot `0000000000`) are removed. A **Privacy settings** link in the footer reopens Google's consent message.
- **Privacy policy** rewritten to cover the visitor statistics and UK consent rules.
- **Visitor statistics** (Azure Application Insights), cookie-free, so no extra cookie banner is needed.
- **Better PDFs:** the server now has fonts sized exactly like Calibri and Cambria, Word's default fonts, so line breaks and page counts match the original more often.
- `swapdoc.co.uk` now redirects to `www`, and the Azure test address is hidden from Google.

### How to deploy

You need the **Azure CLI** (the `az` command) once. In PowerShell:

```powershell
winget install -e --id Microsoft.AzureCLI
```

Then open a **new** PowerShell window and run:

```powershell
cd $HOME\SwapDoc
.\deploy\deploy.ps1
```

The script will:

1. Open your browser to sign in to Azure, if you aren't signed in already.
2. Find the `swapdoc` Container App.
3. Create `log-swapdoc` (where statistics are stored), `appi-swapdoc` (Application Insights) and the **SwapDoc visitors** dashboard, in the same resource group.
4. Build the new code inside Azure (about 5–10 minutes) and switch the site to it.
5. Check that the live site responds.

Run `.\deploy\deploy.ps1` again whenever you change the code. Add `-SkipAnalytics` to deploy code only.

**Cost:** Application Insights is free for the first 5 GB of data a month. SwapDoc will use a tiny fraction of that. As a safety net, the template stops collecting data for the day after 0.5 GB.

---

## 3. Use the visitor dashboard

**Open it:** portal.azure.com → search **Workbooks** → **SwapDoc visitors**. The deploy script also prints a direct link. Click the pin icon to add it to your Azure home dashboard.

What it shows (choose 24 hours, 7, 30 or 90 days at the top):

| Section | Shows |
|---|---|
| Tiles | Visitors, page views, average minutes per visitor, files converted |
| Over time | Visitors and page views per day |
| Where | Map of countries, and the top towns and cities |
| Pages | Views, visitors and **average time on page** for every page |
| How they found you | Google, Bing, other websites, or direct |
| Device and browser | Mobile, tablet or desktop; Chrome, Safari and so on |
| Conversions | Successful conversions per day (Word to PDF and PDF to Word), plus failures and rate limits |
| Latest visits | The last 50 page views, with page, town, source and device |

**Good to know:**
- Data appears 2–5 minutes after a visit.
- **Visitors are counted once per day.** To avoid cookies, each visitor gets an anonymous ID that changes daily, so "returning visitor" isn't measured.
- **Location** is worked out from the visitor's internet address, which Microsoft then discards. It's accurate to roughly the town. Mobile users often show up at their network's city.
- **Ad blockers** stop some visitors being counted (usually 10–30% of tech-savvy audiences). The "Server" table counts every conversion, including those visitors.
- For a live view while testing: **appi-swapdoc → Investigate → Live metrics**.

**Want to build your own charts?** Open **appi-swapdoc → Logs** and try:

```kusto
pageViews
| where timestamp > ago(7d)
| summarize Visitors = dcount(user_Id) by client_CountryOrRegion
| order by Visitors desc
```

---

## 4. Google Search Console and Bing

Your domain is already verified with Google (the `google-site-verification` record is in DNS).

1. Go to **search.google.com/search-console** and open the **swapdoc.co.uk** property.
2. **Sitemaps** → enter `https://www.swapdoc.co.uk/sitemap.xml` → **Submit**. It should list 13 pages.
3. **URL inspection** → paste `https://www.swapdoc.co.uk/word-to-pdf` → **Request indexing**. Repeat for `/pdf-to-word` and `/guides`.
4. Go to **bing.com/webmasters** → **Import from Google Search Console**. That also covers DuckDuckGo and Yahoo.

New pages usually appear in results within a few days to a few weeks. Search Console → **Performance** shows which searches find you.

**Ways to grow traffic later:** add a guide every few weeks (for example "how to compress a PDF" or "how to sign a PDF"), and get a few links from elsewhere (Reddit answers, a Product Hunt or AlternativeTo listing, forum signatures).

---

## 5. AdSense

Your publisher ID `ca-pub-5734256894506579` is already in the site and in `ads.txt`.

### a. Request a review

1. Go to **adsense.google.com** → **Sites**.
2. If `swapdoc.co.uk` shows **Needs attention**, **Getting ready** or **Site down or unavailable**, finish **Part 1** first. AdSense checks the domain without www, which is currently the IONOS parking page. Then click **Request review**.
3. Check **ads.txt status** says **Authorised**. This can take a few days after deploying.

Common rejection reasons and where they're now covered:

| Reason | Status |
|---|---|
| Site down or unavailable | Fixed by Part 1 |
| Low-value content | 13 pages, including 5 original guides and 2 detailed tool pages |
| Missing privacy policy | `/privacy`, updated |
| Hard to navigate | Menu at the top; About, Contact and Terms in the footer |

If it's still rejected for "low-value content", add two or three more guides and request another review after a couple of weeks.

### b. Consent message (required for UK and EU visitors)

Google requires a certified consent tool for UK and EEA visitors, and Google offers one free.

1. AdSense → **Privacy & messaging** → **European regulations** → **Create message**.
2. Select `swapdoc.co.uk`, use the default **Consent** / **Manage options** buttons, and set the privacy policy link to `https://www.swapdoc.co.uk/privacy`.
3. **Publish**.
4. Also publish the **US state regulations** message if you want US personalised ads.

The footer link **Privacy settings** reopens this message so visitors can change their choice. That's a legal requirement, and it's already built in.

### c. Turn on ads

- **Auto ads (easiest):** AdSense → **Ads** → **By site** → `swapdoc.co.uk` → switch on **Auto ads**. Google places ads itself. Nothing to change in the code.
- **Fixed ad boxes (optional):** create two **Display ads** units under **Ads → By ad unit**, then add their slot numbers to the Container App. In Azure → **swapdoc** → **Containers** → **Environment variables**, add `AD_SLOT_TOP` (box under the converter) and `AD_SLOT_CONTENT` (box between sections), then **Save as a new revision**. No code change needed.

---

## Files in this project

| File | What it is |
|---|---|
| `app.py` | The website: pages, conversion, redirects, `sitemap.xml`, `ads.txt` |
| `content.py` | List of pages and guides, with titles and descriptions. Add new guides here |
| `templates/` | Page layouts. `base.html` is shared by every page; `guides/` holds the articles |
| `static/` | Stylesheet, scripts, icons and the link-preview image |
| `infra/analytics.json` | Azure template for Application Insights and the dashboard (built by `infra/build_template.py`) |
| `deploy/deploy.ps1` | One-command deploy |

### Adding a guide

1. Copy `templates/guides/doc-vs-docx.html` to `templates/guides/<new-slug>.html` and write the article.
2. Add an entry to `GUIDES` in `content.py` (slug, title, description, dates).
3. Run `.\deploy\deploy.ps1 -SkipAnalytics`. The menu, guide list and sitemap update automatically.
