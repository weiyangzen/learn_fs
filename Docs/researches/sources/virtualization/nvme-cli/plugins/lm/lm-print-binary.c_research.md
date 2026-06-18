# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print-binary.c

This file implements the binary output backend for LM plugin display operations.

Behavior:
- `binary_controller_state_data()` dumps the supplied controller-state buffer with `d_raw()`.
- `binary_controller_data_queue()` dumps the raw `nvme_lm_ctrl_data_queue_fid_data` structure.
- Exposes `lm_get_binary_print_ops()`, which stores the active print flags and returns the static `lm_print_ops` table.

Role:
- This is one of the strategy backends selected by `lm-print.c` when output flags include `BINARY`.
