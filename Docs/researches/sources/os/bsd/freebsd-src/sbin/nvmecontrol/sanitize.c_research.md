# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/sanitize.c

Purpose: Implements `nvmecontrol sanitize` for NVMe sanitize operations and status polling.

Key behavior:
- Registers top-level `sanitize`.
- Supports sanitize actions: `exitfailure`, `block`, `overwrite`, `crypto`, plus intended numeric compatibility.
- Supports AUSE, NDAS, OIPBP, overwrite pass count, overwrite pattern, and report-only mode.
- Normalizes namespace devices to controllers.
- Checks controller sanitize capabilities before starting block erase, overwrite, or crypto erase.
- Refuses to sanitize one namespace when the controller reports multiple namespaces.
- Submits `NVME_OPC_SANITIZE`, then polls `NVME_LOG_SANITIZE_STATUS` until completion/failure/non-progress status.

Dependencies:
- `read_controller_data()`, `read_logpage()`, `open_dev()`, and `get_nsid()`.
- NVMe sanitize command/status constants.

Research notes:
- The numeric `sanact` parsing expression appears to assign a boolean result of `strtol(...) != 0` rather than the parsed numeric value due to operator precedence. Named actions are unaffected.
