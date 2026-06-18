# File Research: sources/virtualization/nvme-cli/plugins/inspur/inspur-nvme.h

This header registers the Inspur nvme-cli plugin.

Registered plugin:
- Name: `inspur`
- Description: `Inspur vendor specific extensions`
- Version: `NVME_VERSION`

Registered command:
- `nvme-vendor-log`: calls `nvme_get_vendor_log` and retrieves/displays the Inspur vendor log.

It uses the standard nvme-cli plugin macro pattern with `CMD_INC_FILE`, `PLUGIN`, `COMMAND_LIST`, `ENTRY`, and final `define_cmd.h` inclusion.
