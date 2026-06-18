# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysdc_impl.h

## Purpose
Defines private implementation state for SDC, including per-processor-set duty-cycle accounting, per-thread class data, active-thread hash buckets, and class-entry parameters.

## Main Interfaces
- `sysdc_pset_t`: tracks SDC state for a CPU partition, including thread references, on-processor time, break decisions, and debugging counters.
- `sysdc_t`: per-thread SDC data stored via `t_cldata`, including target duty cycle, priority range, associated processor set, timing bases, sleep/update counters, computed priorities, and debug fields.
- `sysdc_list_t`: hash bucket for active SDC threads with a lock and cache-line padding.
- `sysdc_params_t`: arguments passed to `CL_ENTERCLASS()`.
- `SYSDC_DC_MAX`: maximum valid duty-cycle percentage.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/time.h`, `sys/list.h`, and `sys/sysdc.h`. It references `struct _kthread` and `struct cpupart`, tying it to the scheduler, CPU partitioning, and per-thread scheduling-class data.

## Research Notes
Locking comments are part of the contract: fields are protected by `sdl_lock`, `thread_lock()`, or coordination between the thread and `sysdc_update()`.
