# File Research: sources/virtualization/nvme-cli/nvme-print-binary.c

This file implements the binary output backend for nvme-cli's print abstraction. Instead of formatting NVMe structures as text or JSON, its callbacks dump the raw bytes with `d_raw()`.

Public API:
- `struct print_ops *nvme_get_binary_print_ops(nvme_print_flags_t flags)`: sets `binary_print_ops.flags` and returns the singleton binary print operation table.

Main behavior:
- Most callbacks are small adapters that cast a typed NVMe structure to `unsigned char *` and pass a byte length to `d_raw()`.
- Fixed-size structures use `sizeof(*ptr)`.
- Variable-size logs use caller-supplied lengths or lengths derived from little-endian fields inside the returned NVMe structure.
- Unsupported or non-binary-relevant print operations are intentionally set to `NULL` in the `print_ops` table.

Covered output families:
- Identify data: controller, namespace, command-set independent namespace, NVM namespace, ZNS controller/namespace, UUID list, NVM set list, domain list, namespace granularity, namespace descriptors.
- Logs: error, firmware slot, SMART, supported logs, endurance, ANA, self-test, sanitize, LBA status, persistent event, reservation notification, telemetry-related aggregate/event logs, FDP logs, media unit, capacity, management address, rotational media, reachability, discovery, host discovery, AVE discovery, pull-model DDC request, power measurement, and ZNS changed zones.
- Other binary outputs: controller registers, reservation report, directive buffers, feature data buffers, discovery log records, and effects-log list entries.

Notable length handling:
- `binary_phy_rx_eom_log()` computes output length from `hsize`, and when measurement is complete includes `dsize * nd`.
- `binary_discovery_log()` dumps the discovery log header plus `numrec` discovery entries.
- `binary_dispersed_ns_psub_log()` includes `numpsub * NVME_NQN_LENGTH`.
- Host/AVE/pull-model discovery logs use total-length fields from the structure.
- Zone reports, ANA logs, boot partition logs, LBA status, FDP config/usage/status, and several aggregate logs rely on a size passed by the caller.

Integration role:
- Selected by `nvme-print.c` when binary output is requested.
- Shares the same `struct print_ops` interface as stdout and JSON printers, allowing command code to remain mostly output-format agnostic.
- Depends on `nvme-print.h`, `logging.h`, and `common.h`, including `d_raw()`, endian helpers, NVMe structure definitions, and `list_head` iteration.

State and ownership:
- Uses one static `binary_print_ops` table.
- `nvme_get_binary_print_ops()` mutates only the table's `flags` field before returning it.
- The backend does not allocate, transform, or retain command data.

Risk notes:
- Binary output correctness depends almost entirely on exact length selection. A too-small length truncates data; a too-large length can expose uninitialized or unrelated memory.
- Several lengths are derived from device-provided little-endian fields, so callers must ensure buffers are at least that large before invoking the print callback.
- Because many `print_ops` entries are `NULL`, new command output paths must either tolerate absent binary callbacks or add matching binary handlers.
- The singleton operation table is simple but not isolated per caller; concurrent use with different flags would share mutable state.
