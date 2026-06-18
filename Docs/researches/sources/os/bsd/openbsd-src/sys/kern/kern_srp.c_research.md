# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_srp.c

Purpose: Implements shared reference pointers with garbage collection using hazard pointers on multiprocessor systems, with simpler behavior on uniprocessor builds.

Key behavior:
- `srp_init()`, `srp_gc_init()`, and `srpl_rc_init()` initialize SRP references and destructor/refcount state.
- Locked variants `srp_swap_locked()`, `srp_update_locked()`, and `srp_get_locked()` assume external update serialization.
- MP `srp_swap()` uses atomic pointer swap; `srp_update()` increments GC refcount for new values and starts GC for replaced values.
- `srp_enter()` reserves a per-CPU hazard record and reads a stable pointer.
- `srp_follow()` switches from one hazard-protected pointer to another.
- `srp_leave()` clears the hazard pointer.

GC model:
- `srp_v_referenced()` scans all CPUs' hazard records for a specific `srp` and value.
- If unreferenced, `srp_v_dtor()` calls the destructor and releases the GC refcount.
- If still referenced, `srp_v_gc_start()` allocates a context and retries via timeout until safe.
- `srp_finalize()` waits until a raw value is absent from all hazard records.

Filesystem relevance:
- SRP is a kernel pattern for read-mostly pointer publication and deferred free, useful for networking/VFS-style tables where readers avoid heavy locks.
