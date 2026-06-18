# File Research: sources/virtualization/nvme-cli/logging.c

This file implements nvme-cli logging hooks for libnvme passthrough commands and NVMe-MI requests/responses.

Global state:
- `int log_level` controls verbosity.
- Static `struct submit_data sb` stores one command’s start/end timestamps.

Public functions:
- `is_printable_at_level(int level)` returns true when `log_level >= level` and CLI output format is `"normal"`.
- `map_log_level(int verbose, bool quiet)` maps CLI verbosity to libnvme levels: quiet or zero verbosity -> `LIBNVME_LOG_ERR`, one `-v` -> `LIBNVME_LOG_INFO`, higher -> `LIBNVME_LOG_DEBUG`.
- `nvme_submit_entry()` zeroes timing state and records start time at debug level.
- `nvme_submit_exit()` records end time and prints command fields, result, error, and latency at debug level.
- `nvme_decide_retry()` is intended as retry decision callback for passthrough errors.
- `nvme_mi_submit_entry()` prints NVMe-MI admin request fields and records timing at debug level.
- `nvme_mi_submit_exit()` prints NVMe-MI response result/status and latency at debug level.

Internal formatting:
- `nvme_show_common()` prints common `libnvme_passthru_cmd` fields.
- `nvme_show_command()` adds result and error.
- `nvme_show_latency()` prints elapsed microseconds.
- `nvme_show_req_admin()` converts an NVMe-MI admin request header into passthrough-like fields.
- `nvme_show_req()` and `nvme_show_resp()` switch on NVMe-MI message type and currently handle admin messages.

Integration:
- Includes `logging.h`, `util/sighdl.h`, and `nvme-print.h`.
- Uses global `nvme_args` for output format and retry settings.
- Uses libnvme and libnvme-mi callback signatures.

Risk and maintenance notes:
- `sb` is a single static object, so concurrent submissions would overwrite timing state.
- `nvme_decide_retry()` appears logically inconsistent: it returns false when retries are enabled (`!nvme_args.no_retries`) and its error condition cannot return true for either `-EAGAIN` or `-EINTR` as written. This deserves review if retry behavior matters.
- `nvme_log_retry(errno)` logs global `errno`, not necessarily the passed `err`.
