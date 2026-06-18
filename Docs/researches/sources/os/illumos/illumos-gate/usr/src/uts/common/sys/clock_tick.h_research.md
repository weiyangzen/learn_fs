# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/clock_tick.h

This header defines data structures for parallelized clock tick accounting. `clock_tick_cpu_t` tracks per-CPU softint handle, pending tick work, lbolt snapshot, and CPU scan range; `clock_tick_set_t` tracks shared ranges.

It defines CPU offline and xcall-safety macros, maximum CPUs per tick-processing unit, weak softint hooks, `clock_tick`, `membar_sync`, and `hires_tick`.
