# sources/user-network-fs/nfs-ganesha/src/include/export_mgr.h

## Purpose
`export_mgr.h` declares the export manager: the in-memory registry, locking protocol, lookup APIs, mount/unmount work, reference handling, and config hooks for NFS exports.

## Important APIs, Types, And Functions
`struct gsh_export` represents an export with list/tree nodes, state/lock/share lists, root and junction object handles, parent/mounted export links, FSAL export pointer, full and pseudo paths, QoS fields, read/write size limits, filesystem ID, permissions, refcount, lock, options, export ID, status, pNFS marker, mount/update flags, and config generation. Admin helpers are `EXPORT_ADMIN_LOCK`, `EXPORT_ADMIN_UNLOCK`, `EXPORT_ADMIN_TRYLOCK`, `is_export_admin_counter_valid`, and `is_export_update_in_progress`. Public APIs allocate/insert/get/find/mount/unmount/remove/iterate exports, manage references, revert and queue mount/unexport work, prune/remove exports, initialize stats time, handle async delegation transitions, and parse export ID lists.

## Control Flow
Configuration creates or updates exports through config blocks in `support/exports.c`. `alloc_export` creates a referenced export; commit paths validate FSAL/export parameters, initialize roots, mount into pseudo-fs, insert into the export AVL/list registry, and drop config references. Runtime lookups fetch by ID, path, pseudo path, or tag. Updates take `export_admin_mutex`, increment `export_admin_counter` before and after mutation, and use work queues for mount/unexport cleanup.

## State And Persistence
Export state is live process memory backed by FSAL object handles and refcounted path strings. `config_gen` records which parse-tree generation last touched an export. Export definitions persist in the configuration source, not in this header. `nfs_stats_time` captures stats timing.

## Dependencies And Integration Points
It depends on list/AVL/atomic utilities and `fsal.h`. It integrates tightly with `support/exports.c`, pseudo-fs construction, `op_ctx`, FSAL export creation, NFS state lists, pNFS helpers, QoS, conditional logging export ID filters, and DBus export update paths.

## Risks
The lock hierarchy matters: export admin updates use a mutex/seqlock pattern, while individual exports have rwlocks and RCU-refcounted paths. Incorrect reference handling can free exports while objects still point at them. The admin counter is non-atomic by design, so it is advisory and can have false negatives. Update paths must preserve static config fields versus atomically changeable fields and must avoid ABBA deadlocks with `export_opt_lock`.

## Test Signals
Tests should cover export allocation/refcounting, duplicate export IDs, lookup by ID/path/pseudo/tag, mount/unmount work queues, dynamic add/update/remove, seqlock retry detection, stale export shortcuts, path ref acquisition/release, FSAL max read/write adjustment, pNFS export handling, and config reload pruning/remounting.
