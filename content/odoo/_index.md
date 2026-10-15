---
# The `odoo` taxonomy's own page (/erp/odoo/, a bare list of versions) isn't rendered:
# the version chips on /erp/ replace it, and content/erp/_index.md redirects /erp/odoo/ to /erp/.
# The per-version pages (/erp/odoo/18.0/ ...) are still built.
title: "Odoo versions"
build:
  render: never
  list: never
---
