# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-nvme.h

Registers the `solidigm` nvme-cli plugin.

Key details:
- Plugin version: `1.22`.
- Uses `PLUGIN(NAME(...), COMMAND_LIST(...))`.
- Exposes commands for Solidigm identify, SMART, internal logs, garbage collection, market log, latency tracking, telemetry parsing, log page directory, temperature stats, drive info, OCP plugin version, and workload tracker.
- Also exposes compatibility/OCP redirect commands.

Notable command names:
- `smart-log-add`
- `vs-smart-add-log`
- `vs-internal-log`
- `latency-tracking-log`
- `parse-telemetry-log`
- `log-page-directory`
- `cloud-SSDplugin-version`
- `workload-tracker`

One entry has a trailing space in the command string: `"clear-pcie-correctable-errors "`.
