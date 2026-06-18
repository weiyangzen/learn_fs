# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_debug.h

This legacy RDS debug header defines logging levels and debug print entry points.

Core definitions:
- Label is `"RDS"`.
- Levels L0-L5 distinguish major errors, admin-facing info, progressively verbose debug, and excessive trace.
- `RDS_LOG_LINTR` is reserved for interrupt/softint/taskq/timeout-context messages.
- In DEBUG builds, high-volume macros map to real functions; otherwise L3-L5/intr debug macros compile out.
- L0-L2 functions are always declared and mapped.

Risk-sensitive invariants:
- Non-DEBUG builds still retain lower-level logging.
- Interrupt-context logging has a separate macro to avoid misuse of normal debug paths.
