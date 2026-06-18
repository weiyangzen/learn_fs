# File Research: sources/virtualization/nvme-cli/plugins/dell/dell-nvme.c

- Purpose: Dell vendor identify-controller decoder.
- Data layout: interprets vendor bytes as three 16-bit version components plus array-name bytes.
- Output: prints or JSON-encodes `array_name` and `array_ver`; empty array names are rendered as `NULL`.
- Integration: command handler delegates normal identify-controller retrieval to shared `__id_ctrl()` with Dell-specific vendor callback.
