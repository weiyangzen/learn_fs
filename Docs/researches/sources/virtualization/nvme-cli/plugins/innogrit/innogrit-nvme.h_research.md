# File Research: sources/virtualization/nvme-cli/plugins/innogrit/innogrit-nvme.h

This header declares the Innogrit plugin command table for nvme-cli’s command-generation system.

Registered plugin:
- Name: `innogrit`
- Description: `innogrit vendor specific extensions`
- Version: `NVME_VERSION`

Registered commands:
- `get-eventlog`: calls `innogrit_geteventlog`
- `get-cdump`: calls `innogrit_vsc_getcdump`

The file follows the usual nvme-cli plugin pattern:
- Sets `CMD_INC_FILE` to `plugins/innogrit/innogrit-nvme`.
- Uses a multiple-read include guard compatible with command-table generation.
- Includes `cmd.h` before `PLUGIN(...)`.
- Includes `define_cmd.h` at the end.
