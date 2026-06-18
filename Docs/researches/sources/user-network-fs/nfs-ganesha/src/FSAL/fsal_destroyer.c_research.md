## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_destroyer.c

### Purpose
`fsal_destroyer.c` implements server shutdown and emergency cleanup for loaded FSALs. It walks the global FSAL registry, releases lingering handles, pNFS data servers, exports, module references, local filesystem tracking, context refstrings, and locks.

### Important APIs, Types, And Functions
`destroy_fsals` is the main orderly teardown entry point. `emergency_cleanup_fsals` calls each FSAL module's emergency cleanup hook. Internal helpers are `shutdown_handles`, `shutdown_pnfs_ds`, and `shutdown_export`.

### Control Flow
`destroy_fsals` iterates `fsal_list` with safe list traversal. For each FSAL it releases objects on `m->handles`, releases pNFS DS objects on `m->servers`, releases every export on `m->exports`, forcibly zeroes unexpected nonzero module refcounts, and invokes `m->m_ops.unload`. After all modules, it calls `release_posix_file_systems`, `destroy_ctx_refstr`, and `destroy_fsal_lock`. `shutdown_pnfs_ds` also zeroes unexpected DS refcounts before calling `ds_release`.

### State And Persistence
This file destroys process-global runtime state. It mutates FSAL refcounts, DS refcounts, export lists, handle lists, module list membership through unload callbacks, local filesystem registries, and FSAL locks. It does not persist state outside the process.

### Dependencies And Integration Points
It depends on `fsal_private.h` for `fsal_list` and lock lifecycle, `fsal_commonlib` and localfs cleanup for shared FSAL resources, and export/core headers for export references. It relies on method vectors initialized in `default_methods.c` and FSAL-specific overrides for actual release behavior.

### Risks
The destroy path intentionally masks refcount leaks by storing zero before unload; that helps shutdown complete but can hide use-after-free risks in stackable FSALs. Release callbacks must tolerate being called during global teardown and with lingering references. `destroy_fsals` does not visibly lock `fsal_lock` while iterating `fsal_list`, so shutdown assumes no concurrent module registration/unregistration. If a default or buggy release method is installed, lingering handles or DS objects may not release backend resources.

### Test Signals
Tests should simulate FSALs with exports, handles, DS objects, nonzero refcounts, static and dynamic unload behavior, and emergency cleanup hooks. Shutdown tests should assert release ordering, list drainage, local filesystem registry cleanup, and logging of leaked references.
