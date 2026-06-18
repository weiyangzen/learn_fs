# sources/object-store/daos/src/vos/vos_common.c

## Purpose
`vos_common.c` provides shared VOS runtime glue: module initialization, TLS setup, standalone self-mode setup, telemetry allocation, transaction begin/end wrappers, timestamp-cache helper behavior, and media-free helpers. It is the layer that binds VOS to DAOS server module registration, PMDK/umem transactions, BIO/NVMe contexts, RAS notifications, object-cache TLS state, and DTX transaction publishing.

## Important APIs, Types, And Functions
- `struct vos_self_mode` stores standalone-mode TLS, BIO xstream context, NVMe initialization state, a mutex, and a reference count.
- `vos_report_layout_incompat()` reports incompatible durable layout versions through RAS.
- `vos_tls_get()` and `vos_xsctxt_get()` hide the distinction between server TLS and standalone self-mode.
- `vos_ts_add_missing()` fills negative timestamp-cache entries for short-circuited dkey/akey paths.
- `vos_bio_addr_free()` frees SCM offsets through `umem_free()` and NVMe extents through `vea_free()`.
- `vos_tx_begin()` and `vos_tx_end()` wrap umem transactions and DTX handle publication, validation, cleanup, and object eviction on abort.
- `vos_tls_init()` / `vos_tls_fini()` allocate and destroy per-xstream VOS object cache, pool/container handle hashes, transaction descriptor, timestamp table, GC pool list, and telemetry nodes.
- `vos_mod_init()` registers pool/container/object/DTX btree classes and initializes ilog, pool settings, PMDK logging, aggregation thresholds, and environment-driven feature switches.
- `vos_self_init_ext()` / `vos_self_fini()` initialize standalone ABT, NVMe, sys DB/SMD, VOS module state, and BIO xstream context.
- `vos_metrics_alloc()` creates aggregation, space, checkpoint, WAL, cache, VEA, and GC telemetry.

## Control Flow
Module startup enters `vos_mod_init()`, attaches the PMDK log, initializes pool settings, registers container, DTX, object, and object-tree btree classes, initializes ilog support, then reads environment variables such as `DAOS_VOS_AGG_THRESH`, `DAOS_DKEY_PUNCH_PROPAGATE`, `DAOS_SKIP_OLD_PARTIAL_DTX`, and `DAOS_VOS_AGG_GAP`. Server mode gets TLS through `dss_module_key`; standalone mode uses `vos_self_init_ext()`, which serializes global setup with `self_mode.self_lock`, initializes ABT and NVMe, opens the system DB, initializes SMD, allocates BIO context, and honors `DAOS_EVTREE_MODE`.

The transaction path starts with `vos_tx_begin()`. Without a DTX handle it directly begins an umem transaction and checks whether a referenced object was evicted during a possible yield. With a DTX handle it marks the handle as the current TLS DTX and records that the local transaction started. `vos_tx_end()` is the matching exit path. It accumulates SCM/NVMe reservations into the DTX handle, waits until the final operation in a multi-modification DTX, calls `vos_dtx_prepared()` for real non-local DTXs, publishes allocations on success, ends the umem transaction, validates the DTX if required, updates active/solo DTX state, and cancels allocations plus DTX state on error.

## State And Persistence Behavior
Most state here is transient TLS or module state, but it coordinates persistent transactions. `vos_tx_publish()` publishes or cancels reserved SCM actions via `vos_publish_scm()` and NVMe block reservations via `vos_publish_blocks()`. `vos_tx_end()` is responsible for ordering durable DTX preparation, allocation publication, and `umem_tx_end()` so metadata and allocation state commit consistently. Local DTX aborts evict every touched object from the object cache to avoid stale pointers after transaction rollback.

Telemetry nodes and handle hashes are in DRAM. The aggregation gap and start epoch are process-global. Standalone self-mode maintains a reference count so repeated users share initialization and the final release drains GC with `gc_wait()` before tearing down BIO, DB, TLS, NVMe, and ABT.

## Dependencies And Integration Points
This file integrates with `vos_internal.h`, `pmdk_log.h`, umem transactions, BIO/NVMe, VEA, DAOS telemetry, RAS, sys DB/SMD, DAOS server module registration, timestamp cache, object cache, DTX, GC, ilog, object tree, and pool/container handle hash helpers. It is called by most VOS mutation paths through `vos_tx_begin()` / `vos_tx_end()` and by module lifecycle code through `vos_srv_module`.

## Risks And Edge Cases
- `vos_tx_publish()` documents a rollback gap for failed NVMe publish after some reservations have already been released from DRAM, which can temporarily leak space until allocator state is reconciled or restart occurs.
- Transaction begin/end may yield; object eviction checks are required to avoid committing through stale cached object pointers.
- `vos_tx_end()` has multiple race paths around `dae_preparing`, delayed abort, solo DTX post handling, validation, and `-DER_INPROGRESS` client retry.
- Standalone initialization is global and reference-counted; partial failure must call `vos_self_fini_locked()` without double-freeing state.
- Environment switches affect aggregation and DTX compatibility semantics, so tests need explicit coverage of default and overridden values.

## Test Signals
Useful tests include transaction success and abort with SCM/NVMe reservations, object eviction during transaction begin, delayed abort while preparing, standalone init/fini reference counting, sys DB init with and without metadata NVMe, telemetry allocation failure tolerance, aggregation-gap bounds parsing, and timestamp missing-entry population for negative lookups.
