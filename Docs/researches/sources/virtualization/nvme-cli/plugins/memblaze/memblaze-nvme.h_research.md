# File Research: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-nvme.h

This header registers the Memblaze nvme-cli plugin.

Registered plugin:
- Name: `memblaze`
- Description: `Memblaze vendor specific extensions`
- Version: `NVME_VERSION`

Registered commands:
- `smart-log-add`
- `get-pm-status`
- `set-pm-status`
- `select-download`
- `lat-stats`
- `lat-stats-print`
- `lat-log`
- `lat-log-print`
- `clear-error-log`
- `smart-log-add-x`
- `lat-set-feature-x`
- `lat-get-feature-x`
- `lat-stats-print-x`
- `lat-log-print-x`
- `perf-stats-print-x`

Role:
- Exposes both legacy Memblaze command names and newer expanded `-x` monitor/log commands implemented in `memblaze-nvme.c`.
