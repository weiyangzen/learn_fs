# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_khelp.c

## Purpose
Implements the FreeBSD kernel helper framework (`khelp`), which lets loadable helper modules register hook callbacks and optional per-object OSD storage. It bridges helper modules with the `hhook` framework and `osd(9)` storage.

## Key Interfaces
- `khelp_register_helper()` / `khelp_deregister_helper()` add and remove helper modules.
- `khelp_init_osd()` / `khelp_destroy_osd()` allocate and release helper-specific OSD payloads.
- `khelp_get_osd()` and `khelp_get_id()` expose helper storage and helper lookup.
- `khelp_add_hhook()` / `khelp_remove_hhook()` wrap `hhook` hook management.
- `khelp_new_hhook_registered()` attaches registered helpers to hook points created later.
- `khelp_modevent()` is the module event entry point for load, quiesce, shutdown, and unload.

## State And Locking
Global helper state is a descending-`h_id` `TAILQ` guarded by `khelp_list_lock`. Each helper has an OSD id, refcount, hook list, class mask, flags, optional UMA zone, and optional module init/destroy callbacks.

## Control Flow
Module load optionally creates a UMA zone for helpers needing OSD, fills helper metadata, runs module init, then registers hooks and list membership. OSD initialization walks matching helpers, allocates per-helper storage with `M_NOWAIT`, and rolls back partial allocation on failure. Deregistration refuses helpers with nonzero OSD refcount and then removes hooks and OSD ids.

## Integration Notes
Depends on `hhook`, `osd`, `uma`, module events, rwlocks, and refcounts. The sorted helper list is intentionally used to make `osd_set()` allocation behavior more efficient.

## Risks
Unload safety depends on accurate OSD refcounting. OSD allocation is nonblocking and may fail, so callers must handle `ENOMEM`. `khelp_add_hhook()` and `khelp_remove_hhook()` do not update the helper's stored hook array, as noted by in-file comments.
