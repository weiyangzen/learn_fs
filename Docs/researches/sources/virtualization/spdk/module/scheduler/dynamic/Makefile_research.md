# File Research: sources/virtualization/spdk/module/scheduler/dynamic/Makefile

Builds the dynamic scheduler module.

Key elements:
- Compiles `scheduler_dynamic.c`.
- Produces `scheduler_dynamic`.
- Uses shared object version `6.0`.
- Uses blank SPDK map file.

Dependencies:
- Always selected by parent scheduler Makefile.

Research notes:
- The scheduler can use the DPDK governor if available but is built independently.
