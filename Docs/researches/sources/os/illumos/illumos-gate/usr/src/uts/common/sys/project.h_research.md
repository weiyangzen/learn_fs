# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/project.h

## Purpose
Defines kernel project state, project resource accounting, project kstats, project lifecycle helpers, and project resource-control handles.

## Main Interfaces
- `kproject_kstat_t`: zone name, usage, and value kstat fields.
- `kproject_data_t`: per-project accounting for shared memory, IPC, locked memory, contracts, crypto memory, and kstats.
- `kproject_t`: project ID, zone ID/pointer, reference count, shares, rctls, list links, subsystem data, pool binding lock, LWP/task/process counters and controls, CPU cap pointer, and extended policy pointer.
- Flags for lookup:
  - `PROJECT_HOLD_FIND`
  - `PROJECT_HOLD_INSERT`
- Kernel routines:
  - `project_init()`
  - `project_hold()`
  - `project_hold_by_id()`
  - `project_rele()`
  - `project_walk_all()`
  - `curprojid()`
- Globals:
  - `proj0p`
  - `rc_project_nlwps`
  - `rc_project_nprocs`
  - `rc_project_ntasks`
  - `rc_project_locked_mem`
  - `rc_project_crypto_mem`

## Dependencies And Relationships
Includes kstat, types, mutex, rctl, IPC resource controls, and zones. Integrates with pools, CPU caps, KLPD policy, and resource controls.

## Research Notes
The first two fields of `kproject_t` must not be reordered. Comments document which subsystem lock protects each quantity.
