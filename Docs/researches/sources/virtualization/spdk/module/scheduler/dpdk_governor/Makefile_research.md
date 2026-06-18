# File Research: sources/virtualization/spdk/module/scheduler/dpdk_governor/Makefile

Builds the DPDK power governor scheduler support library.

Key elements:
- Adds `$(ENV_CFLAGS)`.
- Compiles `dpdk_governor.c`.
- Produces `scheduler_dpdk_governor`.
- Uses shared object version `6.0`.

Dependencies:
- Requires DPDK power support as selected by parent Makefile.

Research notes:
- Provides frequency scaling operations consumed by schedulers.
