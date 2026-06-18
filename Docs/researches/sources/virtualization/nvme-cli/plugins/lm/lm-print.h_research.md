# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-print.h

This header defines the LM print backend interface.

Key type:
- `struct lm_print_ops` with function pointers for:
  - `controller_state_data`
  - `controller_data_queue`
  - stored `nvme_print_flags_t flags`

Declared backends:
- `lm_get_stdout_print_ops()`
- `lm_get_binary_print_ops()`
- `lm_get_json_print_ops()` when `CONFIG_JSONC` is enabled

Fallback behavior:
- If JSON support is not compiled in, `lm_get_json_print_ops()` is an inline stub returning `NULL`.

Public display API:
- `lm_show_controller_state_data()`
- `lm_show_controller_data_queue()`

Role:
- Provides the shared contract between `lm-nvme.c`, the dispatcher, and individual print backends.
