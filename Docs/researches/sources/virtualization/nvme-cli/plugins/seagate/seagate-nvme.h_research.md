# File Research: sources/virtualization/nvme-cli/plugins/seagate/seagate-nvme.h

Seagate plugin command registration header. It defines `CMD_INC_FILE` as `plugins/seagate/seagate-nvme` and registers the `seagate` plugin.

Registered commands:
- `vs-temperature-stats`
- `vs-log-page-sup`
- `vs-smart-add-log`
- `vs-pcie-stats`
- `clear-pcie-correctable-errors`
- `get-host-tele`
- `get-ctrl-tele`
- `vs-internal-log`
- `vs-fw-activate-history`
- `clear-fw-activate-history`
- `plugin-version`
- `cloud-SSD-plugin-version`

The header has minor formatting inconsistencies but is otherwise a standard nvme-cli plugin registration file.
