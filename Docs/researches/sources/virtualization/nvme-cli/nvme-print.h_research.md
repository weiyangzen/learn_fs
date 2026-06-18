# File Research: sources/virtualization/nvme-cli/nvme-print.h

- Purpose: public declaration header for nvme-cli printing, formatting, status, and conversion helpers.
- Core type: defines `struct print_ops`, the large vtable used by stdout, JSON, and binary printers for logs, identify data, topology, messages, status, and key/value output.
- Shared structures: declares `nvme_effects_log_node_t`, `struct nvme_error_log_filter`, and `struct nvme_bar_cap`.
- Output API: declares all `nvme_show_*` wrapper functions implemented in `nvme-print.c`, including identify, log, topology, FDP, ZNS, discovery, and persistent-event helpers.
- Conversion API: declares `nvme_*_to_string()` helpers for commands, logs, features, registers, power, temperature, timestamps, PEL fields, sanitize states, and FDP events.
- JSON integration: conditionally declares `nvme_get_json_print_ops()` when `CONFIG_JSONC` is enabled, otherwise provides a NULL inline fallback.
- Dependency role: included by command/plugin code that should not know the concrete print backend implementation.
