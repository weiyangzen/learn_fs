# File Research: sources/virtualization/nvme-cli/types.h

Defines nvme-cli wrapper argument structure for Get Log.

Key element:
- `struct nvme_get_log_args` carries namespace ID, RAE, LSP, LID, LSI, CSI, offset type, UUID index, log page offset, destination buffer, length, and command result pointer.

Dependencies:
- Includes `<nvme/nvme-types.h>` for NVMe integer and enum types.

Role:
- Local CLI-side argument bundle for Admin Get Log operations.
