# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_pmc.c

Read completely: 368 lines.

## Purpose
Provides kernel-side support glue for the HWPMC subsystem: hook pointers, CPU topology predicates, per-domain buffer header allocation, soft PMC event registration, and initialization of PMC support data.

## Main Elements
- Exposes `pmc_kernel_version`, `pmc_hook`, `pmc_intr`, `hwt_hook`, and `hwt_intr` for optional PMC/HWT module integration.
- Defines per-CPU `pmc_sampled`, global `pmc_ss_count`, global `pmc_sx`, per-CPU soft trapframes, and per-memory-domain PMC buffer headers.
- CPU helper functions report active, disabled, present, primary, maximum CPU count, and invariant active count.
- `pmc_soft_namecleanup()` normalizes soft event names by removing duplicate/trailing underscores and uppercasing.
- `pmc_soft_ev_register()` assigns dynamic soft event codes, reuses vacant slots when the table is full, and warns once if exhausted.
- `pmc_soft_ev_deregister()` clears a registered soft event slot.
- `pmc_soft_ev_acquire()` returns a soft event while holding the spin mutex; `pmc_soft_ev_release()` releases it.
- `init_hwpmc()` clamps the soft-event tunable, allocates the soft-event table, allocates per-domain buffer headers from preferred memory domains, initializes their locks/lists, and counts CPUs per domain.

## Dependencies And Integration
Uses HWPMC option hooks, SMP CPU masks, memory domains, malloc/domainset allocation, spin mutexes, sx locks, trapframes, sysctl, and PMC event definitions. The mutex file also emits HWPMC soft calls for lock contention when hooks are enabled.

## Risk Notes
Hook pointers are optional and require external locking discipline through `pmc_sx`. Soft event registration warns that event-code reuse can race with old users. `pmc_soft_ev_acquire()` intentionally returns with `pmc_softs_mtx` still held, requiring paired release.
