# File Research: sources/virtualization/nvme-cli/plugins/intel/intel-nvme.h

This header registers the Intel nvme-cli plugin.

Registered plugin:
- Name: `intel`
- Description: `Intel vendor specific extensions`
- Version: `NVME_VERSION`

Registered commands:
- `id-ctrl`
- `internal-log`
- `lat-stats`
- `set-bucket-thresholds`
- `lat-stats-tracking`
- `market-name`
- `smart-log-add`
- `temp-stats`

Each command maps to a static implementation in `intel-nvme.c`. The header follows the standard nvme-cli generated-command include pattern.
