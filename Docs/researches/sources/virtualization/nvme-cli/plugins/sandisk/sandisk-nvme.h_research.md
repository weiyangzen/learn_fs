# File Research: sources/virtualization/nvme-cli/plugins/sandisk/sandisk-nvme.h

## Role

`sandisk-nvme.h` is the command registration header for the Sandisk nvme-cli plugin. It follows the nvme-cli plugin macro pattern: set `CMD_INC_FILE`, guard multi-read inclusion, define plugin metadata, list commands, and include `define_cmd.h`.

## Plugin Metadata

The header defines:

- plugin name: `sndk`
- description: `Sandisk vendor specific extensions`
- version: `3.1.3`

The plugin body is created with `PLUGIN(NAME(...), COMMAND_LIST(...))`.

## Registered Commands

The command list exposes the following CLI entries:

- `vs-internal-log`
- `vs-nand-stats`
- `vs-smart-add-log`
- `clear-pcie-correctable-errors`
- `get-drive-status`
- `clear-assert-dump`
- `drive-resize`
- `vs-fw-activate-history`
- `clear-fw-activate-history`
- `vs-telemetry-controller-option`
- `vs-error-reason-identifier`
- `log-page-directory`
- `namespace-resize`
- `vs-drive-info`
- `vs-temperature-stats`
- `capabilities`
- `cloud-SSD-plugin-version`
- `vs-pcie-stats`
- `get-latency-monitor-log`
- `get-error-recovery-log`
- `get-dev-capabilities-log`
- `get-unsupported-reqs-log`
- `cloud-boot-SSD-version`
- `vs-cloud-log`
- `vs-hw-rev-log`
- `vs-device-waf`
- `set-latency-monitor-feature`
- `cu-smart-log`

Each entry maps to a `sndk_*` handler implemented as a static function in `sandisk-nvme.c` when `CREATE_CMD` is defined.

## Dependencies and Integration

The header includes `cmd.h` inside the plugin guard and `define_cmd.h` at the end, matching nvme-cli plugin-generation conventions. `CMD_INC_FILE` is set to `plugins/sandisk/sandisk-nvme`, allowing the command macro infrastructure to re-include the file in different modes.

## Notable Risks

This header intentionally references handler names before normal C declarations; that is part of the nvme-cli macro generation pattern. The user-visible description for `namespace-resize` says `NamespaceDrive Resize`, which appears to be a typo.
