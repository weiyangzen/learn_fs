# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_hhook.c

## Purpose
Implements the helper hook (`hhook`) KPI: kernel subsystems can register hook points, and helper modules can attach callbacks that run at those points. It supports both global and VNET-local hook heads.

## Main Elements
- `struct hhook` stores a callback, optional helper metadata, user data, and STAILQ linkage.
- Global state consists of `hhook_head_list`, per-VNET `hhook_vhead_list`, `hhook_head_list_lock`, and `n_hhookheads`.
- `hhook_run_hooks()` read-locks a hook head and invokes all registered hooks, supplying helper OSD data when `HELPER_NEEDS_OSD` is set.
- `hhook_add_hook()` / `hhook_remove_hook()` modify a single `struct hhook_head`.
- `hhook_add_hook_lookup()` / `hhook_remove_hook_lookup()` apply a helper hook to all currently registered matching hook heads, including virtual instances.
- `hhook_head_register()`, `hhook_head_deregister()`, and lookup/release routines manage hook head allocation, list membership, and refcounts.
- VNET sysinit/sysuninit initializes per-VNET hook lists and forcibly cleans up any leaked virtualized hook heads during VNET teardown.

## Dependencies And Integration
Uses `rm` locks for per-hook-head reader/writer synchronization, a global mutex for hook-head list membership, `refcount` for lifetime safety, kernel helper/module OSD APIs, and VNET infrastructure when `HHOOK_HEADISINVNET` is used.

## Risk Notes
The file is concurrency-sensitive. `hhook_add_hook_lookup()` deliberately snapshots and refcounts hook heads without holding `hhook_head_list_lock` across `M_WAITOK` allocation. `hhook_remove_hook_lookup()` calls `hhook_remove_hook()` while holding the global list lock, so lock ordering with per-head write locks is part of the implicit contract. Misused VNET hook heads are cleaned up at teardown, but only after warning.
