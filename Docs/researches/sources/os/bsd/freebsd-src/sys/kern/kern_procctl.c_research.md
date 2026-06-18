# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_procctl.c

## Purpose
Implements the FreeBSD `procctl(2)` syscall and kernel dispatcher for per-process and process-group controls. It covers protected-process flags, process reapers, subtree signaling, tracing controls, ASLR/protection policy controls, no-new-privs, W^X mapping policy, parent-death signal, and signal-exit logging policy.

## Major Responsibilities
- Validates and dispatches `sys_procctl()` commands through `procctl_cmds_info[]`.
- Implements protected-process toggling with optional descendant inheritance via `protect_set()`, `protect_setchild()`, and `protect_setchildren()`.
- Implements reaper acquire/release/status/PID-list/kill operations.
- Implements tracing and trapcap controls: `trace_ctl()`, `trace_status()`, `trapcap_ctl()`, `trapcap_status()`.
- Implements process hardening controls: `no_new_privs_*`, `protmax_*`, `aslr_*`, `stackgap_*`, `wxmap_*`, `logsigexit_*`.
- Implements parent-death signal get/set for the calling process.
- Applies commands to a single PID or all visible members of a process group through `kern_procctl()`.

## Reaper Logic
- `PROC_REAP_ACQUIRE` marks the calling process as a subtree reaper.
- `PROC_REAP_RELEASE` abandons children unless the process is `initproc`.
- `PROC_REAP_STATUS` reports current reaper PID, ownership flags, real-init status, child count, descendant count, and first descendant PID.
- `PROC_REAP_GETPIDS` snapshots reaper descendants into `procctl_reaper_pidinfo` records.
- `PROC_REAP_KILL` can signal reaper children or a subtree, tracks already-signaled PIDs with `unrhdr`, handles PID reuse via `P2_REAPKILLED`, and avoids using visibility failures as an oracle.

## Locking and Lifetime Model
- Each command declares required tree locking: shared `proctree_lock`, exclusive `proctree_lock`, or no tree lock.
- `kern_procctl_single()` holds and temporarily references target processes with `_PHOLD()` / `_PRELE()`.
- Reaper subtree killing may drop and reacquire `proctree_lock` around process-group `pg_killsx` synchronization.
- Commands needing whole-process-stop exclusion use the `sapblk` hook and `stop_all_proc_block()`.
- Process-group operations iterate `pg_members` under the required tree lock and per-process locks.

## Security Model
- Visibility and debug checks are command-specific through `p_cansee()` or `p_candebug()`.
- Capability mode blocks reaper kill and records `ktrcapfail()` when tracing is active.
- Signal delivery uses `p_cansignal()` or held credentials with `cr_cansignal()`.
- Protection controls require `PRIV_VM_MADV_PROTECT`.
- Many hardening controls require debug permission when modifying another process.

## Key Interfaces
- User entry: `sys_procctl()`.
- Kernel entry: `kern_procctl()`.
- Command metadata: `procctl_cmds_info[]`.
- Reaper support: `reap_acquire()`, `reap_release()`, `reap_status()`, `reap_getpids()`, `reap_kill()`.
- Policy toggles: ASLR, PROTMAX, stackgap, W^X, no-new-privs, tracing, trapcap, parent-death signal, and signal-exit logging.

## Notable Edge Cases
- Some commands are restricted to `P_PID` only through `one_proc`.
- Some commands translate missing process from `ESRCH` to `EINVAL`.
- `PROC_REAP_KILL` may copy out status even on error so callers can see partial kill results.
- `aslr_status()` and `wxmap_status()` temporarily drop the process lock to acquire `vmspace` references.
