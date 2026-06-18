# File Research: sources/virtualization/nvme-cli/plugins/ssstc/ssstc-nvme.c

Implements the SSSTC `smart-log-add` command.

Data model:
- Packed SMART item with key, normalized value, 6-byte raw union, and padding.
- `nvme_additional_smart_log` enumerates SSSTC-specific SMART attributes such as program/erase failures, wear leveling, ECC counts, GC count, RAID recovery failure, in-flight commands, die failures, read disturb, and retention count.

Main behavior:
- Parses namespace, raw binary, and JSON options.
- Fetches log page `0xca` with `nvme_get_log_simple()`.
- Outputs JSON, human-readable table, or raw bytes.

Output details:
- Several fields are decoded as 48-bit raw values.
- Wear-leveling-like fields decode min/max/avg 16-bit values.
- JSON output nests each metric under `"Device stats"`.

Risks/notes:
- Namespace option is displayed but not passed to `nvme_get_log_simple()`.
- JSON uses `json_object_add_value_int()` for `uint64_t raw_val`, which may truncate large values depending on helper implementation.
