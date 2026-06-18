# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print-json.c

This file implements JSON output for LM plugin data structures.

Behavior:
- `json_controller_state_data()` rejects non-zero offsets because it cannot interpret partial controller-state data. For full data, it emits:
  - Top-level controller state version, attributes, NVMe controller state size, and vendor-specific size.
  - Nested NVMe controller state header with version and queue counts.
  - Arrays for I/O submission queues and I/O completion queues, including PRP, queue size, IDs, attributes, and head/tail pointers.
- `json_controller_data_queue()` emits CDQ head pointer and tail pointer trigger.
- `lm_get_json_print_ops()` returns the JSON print-ops table.

Dependencies:
- Uses json-c wrappers from nvme-cli `common.h`.
- Uses little-endian conversions, including 128-bit helper conversion for state sizes.

Role:
- This backend is selected by `lm-print.c` when JSON output is requested and `CONFIG_JSONC` support is present.
