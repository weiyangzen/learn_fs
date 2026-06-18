# File Research: sources/virtualization/nvme-cli/plugins/lm/lm-nvme.c

This file implements the NVMe Live Migration plugin command set.

Registered command implementations:
- `lm_create_cdq()`: creates a Controller Data Queue.
- `lm_delete_cdq()`: deletes a Controller Data Queue.
- `lm_track_send()`: sends Track Send management commands.
- `lm_migration_send()`: sends migration management data.
- `lm_migration_recv()`: receives migration/controller state data.
- `lm_set_cdq()`: sets Controller Data Queue feature `0x21`.
- `lm_get_cdq()`: gets Controller Data Queue feature `0x21`.

Core behavior:
- Uses libnvme initialization helpers such as `nvme_init_lm_cdq_create()`, `nvme_init_lm_cdq_delete()`, `nvme_init_lm_track_send()`, `nvme_init_lm_migration_send()`, and `nvme_init_lm_migration_recv()`.
- Uses `libnvme_exec_admin_passthru()` for live-migration admin commands.
- Uses `nvme_get_features()` and `nvme_set_features()` for CDQ feature operations.
- Uses hugepage allocation for data buffers that are passed to the controller.

Important validation:
- `lm_create_cdq()` requires explicit `--consent` because the code notes CDQs cannot be safely mapped to user space and may cause device writes to invalid memory.
- `lm_track_send()` currently supports only `NVME_LM_SEL_LOG_USER_DATA_CHANGES`, and provides `--start`/`--stop` convenience flags.
- `lm_migration_send()` checks that suspend/resume options do not include controller-state-only fields, and that `SET_CONTROLLER_STATE` has an input file and does not include suspend-only options.
- `lm_migration_recv()` refuses to parse non-zero-offset output unless binary output is requested.

Output handling:
- `lm_migration_recv()` can write raw controller-state data to an output file, or delegate decoded display to `lm_show_controller_state_data()`.
- `lm_get_cdq()` delegates display to `lm_show_controller_data_queue()`.

Notable quirks:
- `lm_create_cdq()` checks `if (!consent)` instead of `if (!cfg.consent)`, so it tests the non-null description string rather than the parsed flag. This appears to bypass the intended consent gate.
- In `lm_migration_recv()`, `fopen()` result is compared with `< 0`; for `FILE *`, the correct failure check is `fd == NULL`.
- The file relies on live-migration definitions from libnvme/nvme headers, so it is a thin CLI/admin-command wrapper rather than a protocol implementation from scratch.
