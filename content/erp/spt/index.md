---
title: "SPT: Syrian Pound Exchange Rates for Odoo"
summary: "Keeps Syrian Pound (SYP) exchange rates in Odoo up to date from Syrian market providers (SP Today)."
date: 2026-10-09
tags: ["odoo", "accounting", "api", "python"]
aliases: ["/projects/spt/", "/odoo/spt/"]
cover:
  image: "feature.png"
  alt: "SPT provider form"
---

Odoo API integration that keeps **Syrian Pound (SYP)** exchange rates up to date from Syrian
market rate providers. The supported provider is **[SP Today](https://sp-today.com)**, and the
design is extensible to other sources.

**Source:** [github.com/yakhras/Odoo-SPT](https://github.com/yakhras/Odoo-SPT) · **License:** LGPL-3 · **Odoo:** 18.0

## Features

- Fetches SYP market rates from the SP Today API (Damascus, Aleppo or Homs)
- One rate provider per company (multi-company safe)
- Choice of price side: **Buy**, **Sell** or **Mid (average)**. Buy and sell are stored on the rate as well.
- Old / new Syrian pound scale (new = old ÷ 100), converted automatically
- Scheduled updates at a configurable interval (days / weeks / months)
- Manual update: an **Update Rates Now** button, plus a wizard for a date range
- Shows the remaining API quota (monthly limit, remaining requests, reset date)
- Coexists with other currency rate providers without conflicts

## Screenshots

Provider configuration:

![Provider form](provider_form.png)

All providers with price side, scale, schedule and remaining API quota:

![Provider list](provider_list.png)

Update several providers at once:

![Update wizard](update_wizard.png)

Resulting SYP rates:

![SYP rates](syp_rates.png)

## Installation

```bash
git clone -b 18.0 https://github.com/yakhras/Odoo-SPT.git
```

Restart Odoo, update the apps list, and install **SPT**. Full documentation is in the
[repository README](https://github.com/yakhras/Odoo-SPT#readme).
