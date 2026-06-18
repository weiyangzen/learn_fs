# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-nvme.h

This header registers the `lm` nvme-cli plugin for NVMe Live Migration extensions.

Registered plugin:
- Name: `lm`
- Description: `Live Migration NVMe extensions`
- Version: `NVME_VERSION`

Registered commands:
- `create-cdq`
- `delete-cdq`
- `track-send`
- `migration-send`
- `migration-recv`
- `set-cdq`
- `get-cdq`

The command table maps each CLI verb to the corresponding static implementation in `lm-nvme.c`.
