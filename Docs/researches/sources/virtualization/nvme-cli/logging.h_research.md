# File Research: sources/virtualization/nvme-cli/logging.h

This header declares nvme-cli logging callbacks and verbosity helpers.

Exports:
- `extern int log_level;`
- `bool is_printable_at_level(int level);`
- `int map_log_level(int verbose, bool quiet);`
- libnvme passthrough callbacks:
  - `nvme_submit_entry()`
  - `nvme_submit_exit()`
  - `nvme_decide_retry()`
- NVMe-MI callbacks:
  - `nvme_mi_submit_entry()`
  - `nvme_mi_submit_exit()`

Macros:
- `print_info(...)` prints only when `LIBNVME_LOG_INFO` is printable.
- `print_debug(...)` prints only when `LIBNVME_LOG_DEBUG` is printable.

Integration:
- Forward declares libnvme transport and NVMe-MI types to avoid heavy includes.
- Includes `<nvme/lib.h>` for log-level constants and types such as `__u8`.

Risk and maintenance notes:
- The macros use `printf` but the header does not include `<stdio.h>` directly; users likely include it transitively.
