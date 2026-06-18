# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rctl_proc.c

## Purpose

Registers and initializes process-scoped resource controls, including the controls that back legacy `RLIMIT_*` behavior and several System V IPC, event port, and signal queue process limits.

## Key Interfaces and State

- `rctlproc_legacy[RLIM_NLIMITS]` maps legacy rlimit indices to rctl handles.
- `rctlproc_flags[]` and `rctlproc_signals[]` define default local action flags and signals for legacy rlimits.
- Exported handles include `rc_process_msgmnb`, `rc_process_msgtql`, `rc_process_semmsl`, `rc_process_semopm`, `rc_process_portev`, and `rc_process_sigqueue`.
- `rctlproc_default_init()` seeds `init` process defaults for CPU, file size, data, stack, core, file descriptors, and virtual memory.
- `rctlproc_init()` registers all process controls and creates the initial `curproc->p_rctls` set for the scheduler process.

## Control-Specific Behavior

- `process.max-cpu-time` uses `proc_cpu_time_test()` and fires when the passed increment is greater than or equal to the current value.
- `process.max-file-size` updates `p_fsz_ctl` through `proc_filesize_set()`.
- `process.max-stack-size` updates `p_stk_ctl` and records the old stack control in the current LWP so post-syscall handling can adjust user stack bounds.
- `process.max-file-descriptor` updates `p_fno_ctl` and uses `rcop_absolute_test()`.
- `process.max-address-space` updates `p_vmem_ctl`.
- Data and core size use default operations.

## Dependencies

Depends on `rctl.c` registration and rlimit translation helpers, process model fields (`p_fsz_ctl`, `p_stk_ctl`, `p_fno_ctl`, `p_vmem_ctl`), signal constants, system tunables such as `rlim_fd_cur`/`rlim_fd_max`, and legacy System V IPC module variables read via `rctl_add_legacy_limit()`.

## Notes for Future Work

- Architecture-specific stack maxima differ across SPARC, non-SPARC LP64, and non-LP64 builds.
- The stack callback intentionally has special handling for the calling LWP and is not a general safe way to resize another process's stack.
