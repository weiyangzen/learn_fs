# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cap_util.h

This kernel header defines capacity/utilization accounting support built on CPC performance counters and processor-group hardware relationships. It includes per-counter statistics, per-hardware-PG counter info, multiplexed CPC context state, and per-CPU capacity/utilization state.

Exports initialize/finalize the subsystem, program/unprogram CPC on CPUs, update CPU and processor-group statistics, disable/enable accounting globally, and call platform-specific CPC setup. `CU_CPC_ON` checks whether a CPU has active capacity counters.
