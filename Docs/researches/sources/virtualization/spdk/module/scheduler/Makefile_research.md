# File Research: sources/virtualization/spdk/module/scheduler/Makefile

Top-level build dispatcher for scheduler modules.

Key elements:
- Always builds `dynamic`.
- Builds `dpdk_governor` and `gscheduler` only when `DPDK_POWER=y`.
- Emits a clean-time warning when DPDK power support is missing.
- Uses SPDK subdir build infrastructure.

Dependencies:
- DPDK power support gates frequency-governor-based scheduling modules.

Research notes:
- Dynamic scheduler can build without DPDK power; governor-dependent modules cannot.
