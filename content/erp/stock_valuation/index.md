---
title: "Stock Valuation per Warehouse for Odoo"
summary: "Values stock per warehouse in Odoo: each warehouse keeps its own average cost, with cost history, landed costs, revaluation and transfers between warehouses."
date: 2026-10-13
tags: ["odoo", "inventory", "accounting", "python"]
odoo: ["18.0"]
module: stock_valuation
repo: yakhras/Odoo-Stock-Valuation
releases:
  "18.0": "18.0.1.0.2"
notes:
  "18.0": "Odoo 18.0 only: Odoo 19.0 removed the stock valuation layers this module is built on, so a 19.0/20.0 version would be a redesign, not a port."
screens:
  - name: location_costs
    caption: "*Location Costs* (Inventory → Reporting): every product and warehouse cost in one list."
    notes:
      - "The warehouse the cost belongs to."
      - "Its current average cost (AVCO)."
  - name: stock_value
    caption: "Stock per location: the same product is worth 0.44 in one warehouse and 0.72 in the other."
    notes:
      - "The unit value, from the cost of the location's warehouse."
      - "The value of the stock in that location."
  - name: product_costs
    caption: "The product form's *Costs* tab: this product's cost in each warehouse."
    notes:
      - "The tab added by the module."
      - "One line per warehouse with its own cost."
  - name: revaluation
    caption: "The revaluation wizard works on one warehouse at a time."
    notes:
      - "The warehouse to revalue."
      - "The current value of the stock in that warehouse only."
  - name: valuation_layer
    caption: "A valuation layer carries its warehouse, so deliveries are valued at their own warehouse's cost."
    notes:
      - "The warehouse of this layer: here a receipt into the North warehouse."
  - name: exo_transfer
    caption: "A transfer between warehouses: validating the EXO (out) creates the EXI (in) for the destination warehouse."
    notes:
      - "Where the goods go. The value moves with them."
---

An Odoo module that values stock **per warehouse** instead of once per company. Standard Odoo
keeps one average cost per product, so goods bought at different prices in different warehouses
all end up at the same blended cost. With this module, each warehouse keeps its own cost.

**Source:** [github.com/yakhras/Odoo-Stock-Valuation](https://github.com/yakhras/Odoo-Stock-Valuation) · **License:** AGPL-3 · **Odoo:** {{< odoo >}}

## Features

- A separate cost for each product and warehouse, updated with AVCO on every receipt
- A history of every cost change: old and new cost, difference, user and date
- Valuation layers carry their warehouse, so deliveries are valued at their own warehouse's cost
- Stock lists show *Unit Value* and *Value* per warehouse
- Landed costs raise only the receiving warehouse's cost, prorated to the stock that remains
- The revaluation wizard works on one warehouse at a time
- Transfers between warehouses (EXO → EXI) move the value along with the goods
- Covered by 16 automated tests, run by GitHub Actions on every push and before every release

## Download and screenshots

The screenshots use generated demo data; the numbers on them match the notes below each one.

{{< versions >}}

## Installation

Download the zip above, or clone the `18.0` branch. Add the folder to `addons_path`, restart
Odoo, update the apps list and install **Stock Valuation per Warehouse**. Products need an AVCO
costing method; FIFO isn't supported yet. Full documentation and known limitations are in the
[repository README](https://github.com/yakhras/Odoo-Stock-Valuation#readme).
