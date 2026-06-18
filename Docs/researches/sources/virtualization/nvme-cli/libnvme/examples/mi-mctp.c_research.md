# File Research: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp.c

This is a broad NVMe-MI over MCTP example CLI.

Supported target modes:
- Direct endpoint: `<net> <eid>`
- D-Bus scan mode: `dbus`, which discovers known MCTP endpoints and runs the selected action on each.

Supported actions:
- `info`: subsystem info, port info, and health status.
- `controllers`: controller list and per-controller metadata.
- `identify <controller-id> [--partial]`: Identify Controller over MI admin passthrough.
- `get-log-page <controller-id> [<log-id>]`: Get Log Page and hexdump data.
- `admin <controller-id> <opcode> [<cdw10> ...]`: raw MI admin request.
- `security-info <controller-id>`: Security Receive protocol list.
- `get-config [port]`: SMBus frequency and MCTP MTU.
- `set-config <port> <type> <val>`: set SMBus frequency or MCTP MTU.
- `control-primitive <abort|pause|resume|get-state|replay>`: sends MI control primitive.

Key helpers:
- Port-specific printers for PCIe and SMBus port data.
- Controller info printer with PCIe route and PCI IDs.
- Hexdump routines used by log and admin raw actions.
- Security protocol description lookup.
- SMBus frequency string/value mapping.
- Central `do_action_endpoint()` dispatcher.

Integration role:
- Demonstrates most core libnvme MI/MCTP APIs in a single sample utility.
- Useful as reference for endpoint scanning, transport handle creation, admin passthrough, MI data reads, config commands, and control primitives.
