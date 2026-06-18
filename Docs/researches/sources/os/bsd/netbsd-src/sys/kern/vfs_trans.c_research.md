# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_trans.c

Read completely: 1140 lines.

## Purpose
Implements filesystem transaction state tracking, suspension/resume coordination, per-LWP transaction bookkeeping, layered-mount aliasing, and copy-on-write handler registration/execution.

## Main Interfaces
- Initialization/lifecycle: `fstrans_init`, `fstrans_lwp_dtor`, `fstrans_mount`, `fstrans_unmount`.
- Transaction entry/exit: `fstrans_start`, `fstrans_start_nowait`, `fstrans_start_lazy`, `fstrans_done`, `fstrans_held`, `fstrans_is_owner`.
- State control: `fstrans_setstate`, `fstrans_getstate`, `vfs_suspend`, `vfs_resume`.
- COW hooks: `fscow_establish`, `fscow_disestablish`, `fscow_run`.
- DDB diagnostics: `fstrans_dump` when compiled with DDB.

## State And Control Flow
Global state is protected by `fstrans_lock`, with pserialize used for fast transition visibility. Each mount has `fstrans_mount_info` containing current state, refcount, gone flag, owner LWP, lower-mount pointer, and a list of COW handlers. Each LWP has cached `fstrans_lwp_info` entries storing mount, alias, transaction count, COW count, and lock type.

Transactions are either `FSTRANS_SHARED`, blocked while suspending, or `FSTRANS_LAZY`, allowed through `FSTRANS_SUSPENDING` but not fully suspended. Recursive transactions increment per-LWP counters. State changes publish the new state, wait until incompatible active transactions drain, then assign or clear exclusive ownership.

Layered mounts can alias transaction state to a lower mount. Mount info teardown marks entries gone, removes them from the hash, and later clears per-LWP entries when counters and alias counts reach zero.

## Dependencies And Integration
Uses mount structures, pserialize, pool caches, condition variables, deadfs, specfs block-device mount lookup, buffers, and VFS `SUSPENDCTL`. It is used by vnode reclaim/drain paths and by filesystems that need consistent suspension windows.

## Risks And Edge Cases
- Correctness depends on transaction callers pairing `fstrans_start*` and `fstrans_done`; stale counts can block suspension indefinitely.
- Lower-mount aliasing changes which per-LWP entry is charged, so cleanup must maintain alias counts precisely.
- `fstrans_mount_dtor` frees a copied dead mount structure only when refcounts and gone accounting reach expected states.
- COW handler list modification waits for in-flight handlers through pserialize and `fli_cow_cnt`; handler recursion is counted.
- `vfs_suspend` serializes all suspensions with `vfs_suspend_lock` and delegates actual filesystem suspension to `VFS_SUSPENDCTL`.

## Filesystem Relevance
High. This file provides the transaction barrier used to suspend filesystems, protect unmount/reclaim paths, and run COW hooks before buffer writes.
