# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/nvme-cmds-mi.h

## Role

Inline helper header for NVMe Management Interface command initialization.

## Helpers

- `nvme_init_get_log_mi_cmd_supported_effects()`: initializes Get Log Page for MI Commands Supported and Effects.
- `nvme_init_mi_cmd_flags()`: sets passthrough command flags for NVMe-MI, currently encoding the Ignore Shutdown (`ish`) bit.

## Dependencies

Includes `nvme/ioctl.h`, `nvme/nvme-cmds-base.h`, and `nvme/nvme-types-mi.h`.

## Notes

This file is intentionally small. It depends on base command dword definitions for MI admin command flag encoding.
