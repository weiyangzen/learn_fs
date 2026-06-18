
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados.h

## Purpose

`recovery_rados.h` is the shared interface for Ceph RADOS-backed NFSv4 recovery backends. It defines common limits, configuration structures, global RADOS handles/object names, callback argument shapes, key/value helpers, and backend functions used by the kv, ng, and clustered variants.

## Important APIs, types, and functions

- `RADOS_KEY_MAX_LEN` is 21 bytes for a decimal `uint64_t` clientid plus NUL.
- `RADOS_VAL_MAX_LEN` is `PATH_MAX`, used for the client-name plus revoked-handle string.
- `rados_recov_io_ctx`, `rados_recov_oid`, and `rados_recov_old_oid` are shared RADOS IO and object-name state.
- `struct rados_kv_parameter` holds `ceph_conf`, `userid`, `pool`, `namespace`, `grace_oid`, and optional `nodeid`.
- `struct pop_args` bundles `add_clid_entry`, `add_rfh_entry`, and flags describing old/takeover traversal.
- `rados_kv_create_key()` formats `clientid->cid_clientid` into the decimal key.
- The header declares shared KV operations, node-id setup, value creation, traversal callbacks, revoked-handle update, and `takeover_reclaim_reset()`.

## Control flow

The header establishes a common key/value contract: backends derive a RADOS object name, use decimal client IDs as omap keys, and store client identity plus revoked file handles as values. Traversal functions call a backend-specific `pop_clid_entry_t` to repopulate the recovery list.

## State and persistence behavior

Persistent RADOS state is omap data in one or more RADOS objects. Non-clustered kv uses current and old object names; ng uses one object and a grace-period write operation; clustered recovery names objects by grace epoch and node/IP identity. `gsh_refstr` object-name pointers are shared with RCU protection in implementations.

## Dependencies and integration points

This header depends on librados types, `gsh_refstr`, NFS client structures, and recovery hooks from SAL. It is included by all RADOS recovery backend implementations and provides the public entry points that clustered code uses to call lower-level kv helpers.

## Risks and edge cases

The header exposes mutable global state, so backend mixing requires careful one-backend-at-a-time assumptions. `rados_kv_create_key()` asserts the buffer size exactly, making misuse fail fast. Value-size constraints are implicit and callers must avoid appending revoked handles past `PATH_MAX`.

## Test signals

Compile tests should cover all RADOS backend combinations. Unit-level tests can validate key formatting at `UINT64_MAX`, node-id string selection, value limits, and traversal callback argument behavior. Integration tests should check each backend's object naming aligns with the declarations here.
