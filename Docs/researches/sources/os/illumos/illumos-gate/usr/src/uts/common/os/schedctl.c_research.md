# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/schedctl.c

## Purpose

Implements scheduler-control shared pages mapped between kernel and user space. These pages allow libc/libthread and the kernel scheduler to exchange LWP scheduling, preemption, cancellation, signal-blocking, and parking state efficiently.

## Data Model

- Each process has a list of `sc_page_ctl_t` page-control structures in `p_pagep`.
- Each page contains multiple `sc_shared_t` slots plus a bitmap of allocated slots.
- Slots are allocated per LWP and remain user-mapped until process exec/exit cleanup.

## Key Interfaces

- `schedctl()` is the syscall entry. It allocates and maps a shared slot for the current LWP if missing, installs context ops, initializes scheduling fields, and returns the user address.
- `schedctl_lwp_cleanup()` removes context ops for an exiting/execing LWP and frees its slot bitmap entry without unmapping the page.
- `schedctl_proc_cleanup()` unmaps all scheduler-control pages and frees page-control metadata during process exec/exit.
- Context ops `schedctl_save()`, `schedctl_restore()`, and `schedctl_fork()` update state/CPU or remove inherited child mappings.
- Scheduler hooks update or read `sc_nopreempt`, `sc_yield`, class ID/priority, signal-blocking, cancellation, and park flags.
- `schedctl_init()` computes usable page space and bitmap sizes.
- `schedctl_shared_alloc()`, `schedctl_page_lookup()`, `schedctl_map()`, `schedctl_getpage()`, and `schedctl_freepage()` manage page allocation, mapping, lookup, and teardown.

## Locking and Memory

- `p->p_sc_lock` protects process page lists, bitmaps, and slot allocation.
- `p_lock` must not be held during allocation because memory allocation and mapping can sleep.
- Pages are allocated from anonymous memory, mapped into the kernel with `segkp_get_withanonmap()`, mapped into user space with `segvn`, and locked in memory.
- Fork handling unmaps inherited child mappings unless the child is a `vfork()` child borrowing the address space.

## Dependencies

Uses context-operation infrastructure, VM address-space mapping, anonymous memory, segkp/segvn, bitmaps, thread scheduling fields, signal masks, cancellation flags, and process lifecycle hooks.

## Notes for Future Work

- Cleanup deliberately leaves pages mapped after LWP cleanup because user-level adaptive mutex code can rely on stale mappings until process teardown.
- `schedctl_page_lookup()` returns `NULL` for a condition marked as should-not-happen; callers assume a valid page.
