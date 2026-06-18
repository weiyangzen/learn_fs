# File Research: sources/virtualization/spdk/module/scheduler/gscheduler/Makefile

Builds the governor-based scheduler module.

Key elements:
- Compiles `gscheduler.c`.
- Produces `scheduler_gscheduler`.
- Uses shared object version `6.0`.
- Uses blank SPDK map file.

Dependencies:
- Built only when parent Makefile detects DPDK power support.

Research notes:
- Depends on the `dpdk_governor` runtime selection path.
