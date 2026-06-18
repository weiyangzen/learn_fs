# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print.c

This file is the LM print dispatcher.

Behavior:
- Defines an `lm_print()` macro that resolves an `lm_print_ops` table and invokes the requested operation if present.
- `lm_print_ops()` selects:
  - JSON backend when flags include `JSON` or global output format is JSON.
  - Binary backend when flags include `BINARY`.
  - Stdout backend otherwise.
- `lm_show_controller_state_data()` dispatches controller-state rendering.
- `lm_show_controller_data_queue()` dispatches CDQ feature rendering.

Role:
- Centralizes output-format selection so command implementations in `lm-nvme.c` do not need to know backend-specific formatting details.
