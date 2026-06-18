# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_futex.c

## Purpose
Implements NetBSD futex syscalls: userspace-addressed wait/wake synchronization, requeue operations, wake-op atomic update semantics, bitset waits, and Linux-style robust futex list cleanup on LWP exit.

## Main Interfaces
- `futex_sys_init`, `futex_sys_fini`: initialize/finalize global futex rb-trees.
- `do_futex`, `sys___futex`: dispatch `FUTEX_WAIT`, `FUTEX_WAKE`, `FUTEX_REQUEUE`, `FUTEX_CMP_REQUEUE`, `FUTEX_WAIT_BITSET`, `FUTEX_WAKE_BITSET`, and `FUTEX_WAKE_OP`.
- `sys___futex_set_robust_list`, `sys___futex_get_robust_list`: manage per-LWP robust-list head pointers.
- `futex_release_all_lwp`: scans and releases robust futexes for a dying LWP.
- Lookup/refcount helpers: `futex_lookup`, `futex_lookup_create`, `futex_insert`, `futex_hold`, `futex_rele`.

## State And Control Flow
Futex identity is exact, not hash-approximate: private futexes are keyed by `vmspace + va`, and shared futexes by `uvm_voaddr`. Global `futex_tab` holds separate rb-trees for those keys. Each `struct futex` has a refcount, queue lock, waiter queue, abort lock/list, and associated key. Waiters are represented by `struct futex_wait`, with their own mutex/cv, current futex pointer, bitset, and abort flag.

`FUTEX_WAIT` tests the user word before lookup and again under the futex queue lock before enqueueing to avoid missed wakeups. `futex_wake` either wakes matching waiters or transfers them to a second futex for requeue operations, moving references with the waiter. `FUTEX_WAKE_OP` performs a userland atomic compare-and-swap update under queue locks, then wakes one or both queues depending on the comparison.

## Dependencies And Integration
Depends on UVM address/object identity (`uvm_voaddr_*`), user atomic access helpers (`ufetch_int`, `ucas_int`), condition variables, rb-trees, LWP IDs, process/LWP lookup, and robust-list ABI constants.

## Risks And Edge Cases
- The lock order is explicit and delicate: `futex_tab.lock`, futex queue locks ordered by address, waiter locks, and abort locks.
- `futex_wait_abort` handles a lock-order reversal by publishing the waiter on an abort list before taking the queue lock.
- Refcount overflow is treated as `ENFILE`; requeue reference transfer asserts that destination holds cannot fail.
- Robust-list cleanup is best-effort: unmapped, malformed, looping, or racing userspace structures are reported or silently abandoned.
- Priority inheritance is explicitly not supported.

## Filesystem Relevance
Indirect. Futexes are process/VM synchronization primitives used by userspace runtimes and can synchronize filesystem-using applications, but this file does not implement filesystem or vnode behavior.
