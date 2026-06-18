# File Research: sources/virtualization/nvme-cli/plugins/mangoboost/mangoboost-nvme.c

This file implements MangoBoost’s vendor-specific identify-controller extension.

Behavior:
- Defines `nvme_vu_id_ctrl_field`, with three 16-bit fields for a JSON-RPC 2.0 version tuple and reserved padding.
- `mangoboost_id_ctrl()` casts the identify-controller vendor-specific bytes, formats the version as `0x%04x%04x%04x`, and either:
  - adds `json_rpc_2_0_ver` to a JSON root, or
  - prints it to stdout.
- `id_ctrl()` delegates to nvme-cli’s shared `__id_ctrl()` with MangoBoost’s vendor-specific decoder callback.

Role:
- This is a minimal plugin implementation focused entirely on decoding a vendor-specific identify-controller field.
