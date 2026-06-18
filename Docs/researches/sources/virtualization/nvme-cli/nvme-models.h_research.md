# File Research: sources/virtualization/nvme-cli/nvme-models.h

This header declares the product-name lookup API implemented by `nvme-models.c`.

Public API:
- `char *nvme_product_name(const char *devname);`

Integration role:
- Used by nvme-cli printing code to enrich controller output with a PCI-derived product/model name.
- The returned pointer is owned by the caller and should be freed.

Risk notes:
- The header does not document ownership, but the implementation returns allocated memory.
- Any signature change affects output paths that call `nvme_product_name()` while rendering controller information.
