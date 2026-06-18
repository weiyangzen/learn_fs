# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/task.h

## Purpose
Defines illumos task/project membership interfaces, task flags, kernel task accounting state, and userland task ID syscalls.

## Main Interfaces
- Task flags:
  - `TASK_NORMAL`
  - `TASK_FINAL`
  - `TASK_MASK`
  - project purge flags
- Kernel `task_t`: task ID, flags, project, hold count, member process list, usage accounting, resource controls, LWP/process limits, CPU time/ticks, zone, inherited usage, kstats, and commit-list linkage.
- `task_kstat_t`: zonename, usage, and value kstat fields.
- Kernel globals/resource-control handles:
  - `task0p`
  - `rc_task_lwps`
  - `rc_task_nprocs`
  - `rc_task_cpu_time`
- Kernel APIs:
  - task init/create/begin/attach/change/detach/join/hold/release/end
  - lookup by task ID and zone
  - CPU time increment
  - task commit thread init
- Userland APIs:
  - `settaskid()`
  - `gettaskid()`

## Dependencies And Relationships
Includes `sys/param.h`, `sys/types.h`, and `sys/rctl.h`; kernel path includes ID-space, extended accounting, and kmem support. Tied to projects, zones, resource controls, and process membership.

## Research Notes
The header separates public task ID operations from kernel accounting/resource-control internals.
