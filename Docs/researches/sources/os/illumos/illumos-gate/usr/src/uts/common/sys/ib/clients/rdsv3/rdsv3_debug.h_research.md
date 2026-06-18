# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_debug.h

This RDSv3 debug header defines logging levels, debug print macros/functions, trace hooks, and logging lifecycle.

Core definitions:
- Label is `"RDSV3"`.
- Levels L0-L5 and LINTR mirror legacy RDS logging semantics.
- DEBUG builds enable L3-L5 and interrupt debug macros; non-DEBUG builds compile them out.
- L0-L2 print functions remain declared for all builds.
- `rdsv3_trace()`, `rdsv3_vprintk()`, logging initialization/destruction, and printk rate limiting are declared.

Risk-sensitive invariants:
- Interrupt/taskq logging is separated through LINTR.
- Rate limiting is available for high-volume paths.
