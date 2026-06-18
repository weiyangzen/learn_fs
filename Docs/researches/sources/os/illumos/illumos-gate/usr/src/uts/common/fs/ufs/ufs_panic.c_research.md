# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_panic.c

## Overview
`ufs_panic.c` implements UFS fix-on-failure handling. Instead of always escalating filesystem metadata failures to `CE_PANIC`, it can mark the superblock bad, queue a failure record, drive `lockfs` into an error lock, wait for repair activity, optionally unmount, and fall back to panic when recovery is unsafe or impossible.

## Main Responsibilities
- Provide `ufs_fault()` as the panic-path replacement used by UFS callers.
- Maintain the global `ufs_fix` queue of `ufs_failure_t` records.
- Initialize global and per-mount fix-on-failure state through `ufsfx_init()` and `ufsfx_mount()`.
- Track failure state transitions from initialization through queued, try-lock, locked, fixing, fixed, not-fixed, replica, unmount, or panic states.
- Coordinate with `lockfs`, fsck, the UFS hlock thread, and unmount paths.
- Publish poll wakeups for administrative visibility of error/fix state.
- Keep debug-only state names, error names, action names, and queue dumping helpers.

## Key Control Flow
- `ufs_fault_v()` first writes `FSBAD` directly to the superblock buffer, bypassing normal logging semantics, then triages the failure.
- `triage()` refuses recovery when the system is already panicking, the vnode/ufsvfs is missing, mount policy says `onerror=panic`, or accounting/swap usage would deadlock repair.
- Recoverable failures start the `ufsfx_thread_fix_failures` worker if needed, create a failure record with `init_failure()`, and append it with `queue_failure()`.
- `ufsfx_thread_fix_failures()` sleeps on `ufs_fix`, then repeatedly calls `ufsfx_do_failure_q()` until all nonterminal failure records are done or waiting.
- `ufsfx_do_failure_q()` walks the queue, calls the current state's handler, and computes the shortest retry delay needed by active failures.
- `sf_found_queue()` detects replica failures for a filesystem that already has an active failure and chooses panic, replica, or try-lock behavior based on mount flags and `fx_current`.
- `sf_found_trylck()` polls current lockfs status and calls `set_lockfs()` to establish `LOCKFS_ELOCK`.
- `sf_found_lock_fix_cmn()` watches for fsck start/completion by reading the on-disk superblock and lockfs comment, warning when repair is late.
- `sf_found_umount()` attempts `dounmount()` for `onerror=umount` filesystems after error locking.
- Terminal states clear `fx_current`, note success/failure, and schedule possible fix-thread shutdown.

## State and Locking
- `ufs_fix.uq_mutex` protects the global failure queue and worker state.
- Each `ufs_failure_t` has `uf_mutex`; state transitions require it.
- Per-filesystem `vfs_lock` is used opportunistically on panic paths, with counters for lock-violation races.
- Failure records retain defensive copies/pointers for mount name, ufsvfs, vfs, superblock buffer, lockfs state, and retry timings.
- `set_state()` validates allowed transitions against `state_desc[]` and invokes per-state callbacks before committing state.
- `panicstr` short-circuits recovery and moves records to not-fixed behavior.

## Notable Behaviors
- The most restrictive active policy wins: panic, lock-only, lock-and-unmount, or default repair.
- Secondary failures on a filesystem with an active failure become `UF_REPLICA`.
- `fsck_active()` identifies fsck by searching lockfs comments for the `"[pid:"` marker while the filesystem remains error-locked.
- Repair-completion timeout is scaled by filesystem size using `SecondsPerGig`.
- `ufsfx_unmount()` nulls live ufsvfs/vfs pointers in outstanding failure records so delayed processing does not dereference freed mount state.
- `ufsfx_unlockfs()` treats successful unlock during repair as fixed, passing through `UF_FIXING` when needed to preserve transition rules.

## Error Handling and Recovery Boundaries
- Nonrecoverable `lockfs` failures such as `EACCES`, `EPERM`, `EIO`, `EROFS`, or `EDEADLK` escalate to panic unless unmount is explicitly viable.
- Transient `EBUSY`/`EAGAIN` errors defer retry and may infer that repair has started.
- `EINVAL` while locking is treated as already unmounted/not fixed.
- Allocation or validation failures in `init_failure()` fall back to real panic.

## Research Notes
This file is a recovery controller, not a formatting wrapper around panics. Correctness depends on the failure state machine, lock ordering between `ufs_fix`, failure records, `vfs_lock`, and `ul_lock`, and careful avoidance of blocking or recursive repair work on panic-sensitive paths.
