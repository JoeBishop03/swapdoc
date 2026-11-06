"""Builds infra/analytics.json, the Azure template for SwapDoc's visitor statistics.

It creates three things in your resource group:
  * a Log Analytics workspace (where the data is stored, 90 days),
  * an Application Insights resource (collects it), and
  * a Workbook called "SwapDoc visitors" (the dashboard).

Edit the dashboard queries below, then run:  python infra/build_template.py
"""
import json
import os

TR = {"timeContext": {"durationMs": 604800000}, "timeContextFromParameter": "TimeRange"}
AI = {"queryType": 0, "resourceType": "microsoft.insights/components"}


def text(md, name):
    return {"type": 1, "content": {"json": md}, "name": name}


def query(name, title, kql, vis, width="100", size=0, **extra):
    content = {"version": "KqlItem/1.0", "query": kql.strip(), "size": size, "title": title,
               "visualization": vis, **TR, **AI, **extra}
    return {"type": 3, "content": content, "customWidth": width, "name": name}


def bars(*cols, palette="blue"):
    return {"gridSettings": {"formatters": [
        {"columnMatch": c, "formatter": 4, "formatOptions": {"palette": palette}} for c in cols]}}


params = {
    "type": 9,
    "content": {
        "version": "KqlParameterItem/1.0",
        "parameters": [{
            "id": "6c0c6a43-6d43-4b0c-9a35-6b1d1f5a0001",
            "version": "KqlParameterItem/1.0",
            "name": "TimeRange",
            "label": "Time range",
            "type": 4,
            "isRequired": True,
            "value": {"durationMs": 604800000},
            "typeSettings": {
                "selectableValues": [
                    {"durationMs": 86400000}, {"durationMs": 604800000},
                    {"durationMs": 2592000000}, {"durationMs": 7776000000}],
                "allowCustom": True},
        }],
        "style": "pills", **AI},
    "name": "time-range",
}

items = [
    text("# SwapDoc visitors\n"
         "Who's visiting www.swapdoc.co.uk, where from, which pages they read and for how long. "
         "Pick a time range below. Visitors are counted with an anonymous ID that resets daily, "
         "so someone who visits on three different days counts as three visitors. "
         "Visitors with ad blockers may not be counted.", "intro"),
    params,
    query("tiles", "", """
let visitors = toscalar(pageViews | summarize dcount(user_Id));
let views = toscalar(pageViews | count);
let mins = toscalar(customEvents
    | where name == "engaged"
    | summarize s = sum(todouble(customMeasurements["seconds"])) by user_Id
    | summarize avg(s) / 60.0);
let conv = toscalar(customEvents
    | where name == "convert" and tostring(customDimensions["result"]) == "ok"
    | count);
union
    (print Metric = "Visitors", Value = todouble(visitors), Order = 1),
    (print Metric = "Page views", Value = todouble(views), Order = 2),
    (print Metric = "Avg minutes per visitor", Value = round(coalesce(mins, 0.0), 1), Order = 3),
    (print Metric = "Files converted", Value = todouble(conv), Order = 4)
| order by Order asc
| project Metric, Value
""", "tiles", size=4, tileSettings={
        "titleContent": {"columnMatch": "Metric", "formatter": 1},
        "leftContent": {"columnMatch": "Value", "formatter": 12, "formatOptions": {"palette": "auto"},
                        "numberFormat": {"unit": 17, "options": {"style": "decimal",
                                                                  "maximumFractionDigits": 1}}},
        "showBorder": True}),
    query("trend", "Visitors and page views over time", """
pageViews
| summarize Visitors = dcount(user_Id), ['Page views'] = count() by bin(timestamp, {TimeRange:grain})
| order by timestamp asc
""", "timechart"),
    text("## Where visitors are", "where-h"),
    query("map", "Visitors by country", """
pageViews
| where isnotempty(client_CountryOrRegion)
| summarize Visitors = dcount(user_Id) by Country = client_CountryOrRegion
| order by Visitors desc
""", "map", width="50", mapSettings={
        "locInfo": "CountryRegion", "locInfoColumn": "Country",
        "sizeSettings": "Visitors", "sizeAggregation": "Sum",
        "legendMetric": "Visitors", "legendAggregation": "Sum",
        "itemColorSettings": {"type": "heatmap", "colorAggregation": "Sum",
                              "nodeColorField": "Visitors", "heatmapPalette": "blue"}}),
    query("cities", "Top towns and cities", """
pageViews
| where isnotempty(client_City)
| summarize Visitors = dcount(user_Id), ['Page views'] = count()
    by City = client_City, Region = client_StateOrProvince, Country = client_CountryOrRegion
| top 25 by Visitors desc
""", "table", width="50", **bars("Visitors")),
    text("## What they read, and for how long", "pages-h"),
    query("pages", "Pages", """
let time = customEvents
    | where name == "engaged"
    | extend Page = tostring(customDimensions["page"])
    | summarize TotalSecs = sum(todouble(customMeasurements["seconds"])), Readers = dcount(user_Id) by Page;
pageViews
| summarize Views = count(), Visitors = dcount(user_Id) by Page = name
| join kind=leftouter time on Page
| extend AvgSecs = iff(Readers > 0, toint(TotalSecs / Readers), int(null))
| extend ['Avg time on page'] = iff(isnull(AvgSecs), "-", strcat(AvgSecs / 60, "m ", AvgSecs % 60, "s"))
| project Page, Views, Visitors, ['Avg time on page']
| order by Views desc
""", "table", **bars("Views", "Visitors")),
    text("## How they found SwapDoc, and on what", "src-h"),
    query("sources", "Where visitors came from", """
pageViews
| extend Source = tostring(customDimensions["source"])
| where Source != "internal"
| summarize Visitors = dcount(user_Id) by Source = iff(isempty(Source), "unknown", Source)
| top 15 by Visitors desc
""", "table", width="40", **bars("Visitors", palette="green")),
    query("devices", "Device", """
pageViews
| extend Device = tostring(customDimensions["device"])
| summarize Visitors = dcount(user_Id) by Device = iff(isempty(Device), "unknown", Device)
""", "piechart", width="30"),
    query("browsers", "Browser", """
pageViews
| extend Browser = trim(" ", extract(@"^[^\\d]+", 0, client_Browser))
| summarize Visitors = dcount(user_Id) by Browser = iff(isempty(Browser), "Other", Browser)
| top 6 by Visitors desc
""", "piechart", width="30"),
    text("## Conversions", "conv-h"),
    query("conv-trend", "Successful conversions over time", """
customEvents
| where name == "convert" and tostring(customDimensions["result"]) == "ok"
| summarize Conversions = count() by Direction = tostring(customDimensions["direction"]), bin(timestamp, {TimeRange:grain})
""", "timechart", width="60"),
    query("conv-results", "Conversion results", """
customEvents
| where name == "convert"
| summarize Count = count() by Direction = tostring(customDimensions["direction"]), Result = tostring(customDimensions["result"])
| order by Count desc
""", "table", width="40", **bars("Count", palette="orange")),
    query("server", "Server: conversion requests (includes visitors with ad blockers)", """
requests
| where name has "convert"
| summarize Requests = count(),
    Succeeded = countif(resultCode == "200"),
    ['Rate limited'] = countif(resultCode == "429"),
    Failed = countif(toint(resultCode) >= 500),
    ['Avg seconds'] = round(avg(duration) / 1000.0, 1)
""", "table"),
    text("## Latest visits", "recent-h"),
    query("recent", "Last 50 page views", """
pageViews
| top 50 by timestamp desc
| project Time = timestamp, Page = name, City = client_City, Country = client_CountryOrRegion,
    Source = tostring(customDimensions["source"]), Device = tostring(customDimensions["device"]),
    Browser = client_Browser
""", "table"),
]

workbook = {
    "version": "Notebook/1.0",
    "items": items,
    "isLocked": False,
    "fallbackResourceIds": ["__APPINSIGHTS_ID__"],
}

template = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "location": {"type": "string", "defaultValue": "[resourceGroup().location]"},
        "name": {"type": "string", "defaultValue": "swapdoc"},
        "dailyCapGb": {"type": "string", "defaultValue": "0.5",
                       "metadata": {"description": "Stops collecting for the day after this much data, to cap costs."}},
    },
    "variables": {
        "workspaceName": "[concat('log-', parameters('name'))]",
        "appInsightsName": "[concat('appi-', parameters('name'))]",
        "workbookId": "[guid(resourceGroup().id, parameters('name'), 'visitors-workbook')]",
        "workbookJson": json.dumps(workbook, separators=(",", ":")),
    },
    "resources": [
        {
            "type": "Microsoft.OperationalInsights/workspaces",
            "apiVersion": "2022-10-01",
            "name": "[variables('workspaceName')]",
            "location": "[parameters('location')]",
            "properties": {
                "sku": {"name": "PerGB2018"},
                "retentionInDays": 90,
                "workspaceCapping": {"dailyQuotaGb": "[json(parameters('dailyCapGb'))]"},
            },
        },
        {
            "type": "Microsoft.Insights/components",
            "apiVersion": "2020-02-02",
            "name": "[variables('appInsightsName')]",
            "location": "[parameters('location')]",
            "kind": "web",
            "dependsOn": ["[resourceId('Microsoft.OperationalInsights/workspaces', variables('workspaceName'))]"],
            "properties": {
                "Application_Type": "web",
                "IngestionMode": "LogAnalytics",
                "WorkspaceResourceId": "[resourceId('Microsoft.OperationalInsights/workspaces', variables('workspaceName'))]",
                "DisableIpMasking": False,
                "RetentionInDays": 90,
            },
        },
        {
            "type": "Microsoft.Insights/workbooks",
            "apiVersion": "2022-04-01",
            "name": "[variables('workbookId')]",
            "location": "[parameters('location')]",
            "kind": "shared",
            "dependsOn": ["[resourceId('Microsoft.Insights/components', variables('appInsightsName'))]"],
            "properties": {
                "displayName": "SwapDoc visitors",
                "category": "workbook",
                "sourceId": "[toLower(resourceId('Microsoft.Insights/components', variables('appInsightsName')))]",
                "serializedData": "[replace(variables('workbookJson'), '__APPINSIGHTS_ID__', toLower(resourceId('Microsoft.Insights/components', variables('appInsightsName'))))]",
            },
        },
    ],
    "outputs": {
        "connectionString": {
            "type": "string",
            "value": "[reference(resourceId('Microsoft.Insights/components', variables('appInsightsName')), '2020-02-02').ConnectionString]",
        },
        "workbookUrl": {
            "type": "string",
            "value": "[concat('https://portal.azure.com/#@/resource', resourceId('Microsoft.Insights/workbooks', variables('workbookId')), '/workbook')]",
        },
    },
}

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "analytics.json"), "w", encoding="utf-8") as f:
    json.dump(template, f, indent=2)
    f.write("\n")
print("Wrote infra/analytics.json")
