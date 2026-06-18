# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_lock.c

## Purpose
Implements OpenBSD machine-independent kernel lock, mutex primitives, DDB mutexes, and producer/consumer generation locks.

## Main Responsibilities
- Initializes and wraps `kernel_lock`.
- Implements MI multiprocessor ticket-style `__mp_lock` when configured.
- Implements MI mutexes with fast atomic acquire and slow parking/waiter path when configured.
- Provides uniprocessor mutex fallback.
- Provides DDB mutex enter/leave.
- Initializes WITNESS lock metadata.
- Provides `pc_lock` producer/consumer generation protocol.

## Key Entry Points
- `_kernel_lock_init()`, `_kernel_lock()`, `_kernel_unlock()`, `_kernel_lock_held()`.
- `__mp_lock()`, `__mp_unlock()`, `__mp_release_all()`, `__mp_acquire_count()`, `__mp_lock_held()`.
- `mtx_enter_try()`, `mtx_enter()`, `mtx_leave()`.
- `db_mtx_enter()`, `db_mtx_leave()`.
- `pc_sprod_enter/leave()`, `pc_mprod_enter/leave()`, `pc_cons_enter/leave()`.

## Mutex Design
The MP mutex fast path CASes `mtx_owner` from zero to current CPU. The contended path spins briefly, then uses hashed parking lots with waiter records and a low bit in owner state to indicate waiters. IPL raising/restoration is handled per mutex via `mtx_wantipl` and `mtx_oldipl`.

## MP Lock Design
The MI MP lock stores per-CPU recursion depth/ticket and global `mpl_users`/`mpl_ticket`. Lock acquisition takes a ticket and spins until served; recursion is tracked per CPU.

## pc_lock Design
`pc_lock` uses an odd/even generation counter. Producers make generation odd while updating and even after completion; consumers retry if the generation changes or is observed odd.

## Dependencies
Uses atomic operations, interrupt priority control, scheduler spin accounting, WITNESS, DDB, percpu cacheline alignment, and memory barriers.

## Research Notes
This file contains low-level synchronization primitives used by many other files in this group, especially clock/accounting and descriptor/event paths.
