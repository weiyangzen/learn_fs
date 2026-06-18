# File Research: sources/virtualization/nvme-cli/nvme-print.c

- Purpose: central print facade for nvme-cli. It selects stdout, JSON, or binary `print_ops` backends and exposes stable `nvme_show_*` wrappers used by command implementations.
- Backend dispatch: `nvme_print_ops()` chooses JSON when requested globally or by flags, binary for `BINARY`, otherwise stdout. `nvme_print()` suppresses output during `nvme_args.dry_run`.
- String decoding: maps many NVMe enums and fields to user-facing strings, including ANA states, admin/I/O opcodes, sanitize status, persistent event types, FDP events, registers, log page IDs, features, timestamp attributes, temperature units, power measurement fields, write-protect states, and fabrics transport error types.
- Log/identify wrappers: forwards decoded structures for identify controller/namespace, NVM/ZNS identify data, SMART, error, firmware, sanitize, ANA, reservation, FDP, endurance, predictable latency, persistent events, LBA status, supported logs, discovery, topology, and several newer NVMe log pages.
- Register helpers: checks fabrics register validity, optional fabrics registers, CMB/PMR readiness, reads 32-bit or 64-bit MMIO registers, and forwards register values for printing.
- Error reporting: `nvme_show_err`, `nvme_show_io_cmd_err`, `nvme_show_admin_cmd_err`, `nvme_show_status`, and `nvme_show_opcode_status` route negative errno-style errors and positive NVMe status codes to the active printer.
- Device path helpers: `nvme_dev_full_path()` and `nvme_generic_full_path()` resolve namespace names to `/dev/...`, SPDK paths, or generic `ngXnY` paths when present.
- Notable behavior: several conversion functions return static buffers, so callers should treat results as short-lived and not thread-safe.
