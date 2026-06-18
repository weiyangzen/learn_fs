# File Research: sources/virtualization/nvme-cli/plugins/micron/micron-nvme.h

## Role

Command registration header for the Micron nvme-cli plugin. It follows the nvme-cli plugin pattern:

- Undefines and sets `CMD_INC_FILE` to `plugins/micron/micron-nvme`.
- Guards with `MICRON_NVME` and `CMD_HEADER_MULTI_READ`.
- Includes `cmd.h`.
- Defines `PLUGIN(NAME("micron", ...), COMMAND_LIST(...))`.
- Includes `define_cmd.h` at the end.

## Registered Plugin

Plugin name: `micron`.

Description: `Micron vendor specific extensions`.

Version source: `NVME_VERSION`.

## Registered Commands

The header registers all Micron command handlers implemented in `micron-nvme.c`, including firmware download, temperature, PCIe stats, debug log collection, telemetry feature control, NAND/SMART logs, firmware activation history, latency monitoring, SMBus, Hyperscale boot/version/WAF/cloud logs, workload/vendor telemetry logs, SMART/Health, and Identify Controller.

## Dependency Relationship

This header is included by `micron-nvme.c` with `CREATE_CMD` defined, causing the nvme-cli command generation macros to bind command names to C functions. It contains no logic beyond macro-based plugin declaration.

## Notes

- Handler names must remain synchronized with function definitions in `micron-nvme.c`.
- The command names form the user-facing CLI surface for `nvme micron ...`.
