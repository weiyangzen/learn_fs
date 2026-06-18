
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_ng.c

## Purpose

`recovery_rados_ng.c` implements a safer RADOS recovery backend that avoids mutating durable recovery state during grace. It batches all client additions/removals into a pending RADOS write operation while grace is active and commits the clear-plus-updates transaction only when grace ends.

## Important APIs, types, and functions

- Static state: `grace_op` stores the batched write operation and `grace_op_lock` protects it.
- Global flags: `takeover`, `no_cleanup`, and `object_takeover` track takeover mode and cleanup safety.
- `rados_ng_init()` sets node id, creates `<nodeid>_recov`, connects to RADOS, and creates the recovery object.
- `rados_ng_put()` and `rados_ng_del()` either append omap set/remove operations to `grace_op` or perform immediate synchronous writes outside grace.
- `rados_ng_add_clid()` and `rados_ng_rm_clid()` are backend add/remove hooks.
- `rados_ng_pop_clid_entry()` parses the shared value format and imports clients/revoked handles.
- `rados_ng_read_recov_clids_takeover()` reads local or takeover recovery objects.
- `rados_ng_cleanup_old()` creates a `grace_op` with `omap_clear`, commits it to the local/takeover object, releases it, and exits grace mutation batching.
- `rados_ng_backend` exposes the backend hooks and reuses `rados_kv_add_revoke_fh()` and `rados_kv_get_nodeid()`.

## Control flow

Initialization sets a single current recovery object for the node and creates it if needed. On recovery read with no `gsp`, it traverses that object and imports clients. On takeover, it builds either `<ipaddr>_recov` or `node%d_recov`, traverses the selected object, and sets `takeover=true`.

At the grace boundary, `rados_ng_cleanup_old()` allocates `grace_op`, first adding an `omap_clear`. While `grace_op` is non-null, client add/remove calls only append operations to it and return success without RADOS I/O. `rados_ng_cleanup_old()` then operates the write op against the selected recovery object, atomically clearing old records and applying the spooled mutations, releases the op, and sets `grace_op=NULL`. After that, add/remove operations create their own write op and commit synchronously.

## State and persistence behavior

Unlike `rados_kv.c`, this backend has no separate old object. The existing object remains unchanged during grace, preserving crash recovery information. End grace atomically replaces object omap contents through one write op. Values and keys use the shared RADOS KV format.

`grace_op` is process-local state, protected by a mutex. Persistent object names are stored in shared `rados_recov_oid`.

## Dependencies and integration points

The file depends on shared RADOS KV helpers for config/connection/key/value/traversal/revoked-handle behavior, librados write operations, RCU object-name access, and generic recovery backend hooks. It integrates with the same SAL recovery interface as legacy kv but changes the grace commit model.

## Risks and edge cases

- `rados_ng_pop_clid_entry()` uses `strtok(rfh_names, "#")` after `rfh_names = strtok(NULL, "#")`; optional revoked-handle parsing needs null-safety review.
- `no_cleanup` logs and resets but does not return early, so cleanup may still proceed after an object-name setup failure.
- A large grace-period client churn can accumulate a large in-memory RADOS write op.
- `rados_ng_cleanup()` destroys the mutex but does not release a live `grace_op`; lifecycle must ensure end-grace ran or no op exists.
- Reusing `rados_kv_add_revoke_fh()` during grace can perform immediate read-modify-write outside the batched operation, which is a possible semantic mismatch for the safe-by-design model.

## Test signals

Tests should simulate crash before end grace, successful end-grace transaction, add/remove during and after grace, takeover object selection, RADOS write failures, revoked-handle updates during grace, and concurrent add/remove calls. Persistence tests should verify old records remain visible until `end_grace` commits.
