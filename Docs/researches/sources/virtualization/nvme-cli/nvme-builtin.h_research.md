# File Research: sources/virtualization/nvme-cli/nvme-builtin.h

This header defines the nvme-cli built-in command table through the project’s command macro system.

Structure:
- Sets `CMD_INC_FILE nvme-builtin`.
- Includes `cmd.h`.
- Expands `COMMAND_LIST(...)` containing many `ENTRY(command-name, description, function[, alias])` declarations.
- Includes `define_cmd.h` after the list, allowing the command framework to generate declarations/dispatch structures depending on macro context.

Command categories represented:
- Device/topology: `list`, `list-subsys`, `show-topology`, `top`.
- Identify/list commands: controller, namespace, UUID, IOCS, domains, endurance groups, etc.
- Namespace management: create/delete/attach/detach/get ns id.
- Logs: telemetry, firmware, SMART, ANA, errors, effects, endurance, persistent event, reservation, boot partition, power, host discovery, AVE, and many newer log pages.
- Features/properties: get/set feature/property.
- Firmware and passthrough: fw commit/download, admin/io passthru, security send/recv.
- I/O commands: flush, compare, read, write, write zeroes, write uncorrectable, verify, copy, DSM.
- Maintenance: sanitize, reset, subsystem reset, rescan, registers.
- Fabrics commands under `CONFIG_FABRICS`: discover, connect, disconnect, config, DIM.
- Host/security key helpers: host NQN, DHCHAP, TLS key operations.
- Misc: directives, virtual management, RPMB, lockdown, I/O management.
- NVMe-MI commands under `CONFIG_MI`: `nvme-mi-recv`, `nvme-mi-send`.

Integration:
- Central registry for command dispatch and help generation.
- Conditional entries track build-time feature macros generated from Meson config.

Risk and maintenance notes:
- Adding a command requires consistency between this table, implementation function names, help text, and feature guards.
