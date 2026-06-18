
# sources/user-network-fs/nfs-ganesha/src/SAL/recovery/recovery_rados_kv.c

## Purpose

`recovery_rados_kv.c` implements the base RADOS key/value recovery backend and shared utility layer used by other RADOS backends. It persists each NFSv4 client as a RADOS omap key/value entry, supports current/old object recovery, appends revoked delegation handles into values, parses RADOS-specific config, and manages the librados connection.

## Important APIs, types, and functions

- Globals: `clnt`, `rados_recov_io_ctx`, `rados_recov_oid`, `rados_recov_old_oid`, `node_id`, `nodeid`, and `rados_kv_param`.
- Config: `rados_kv_params` and `rados_kv_param_blk` define `RADOS_KV` block parsing.
- `rados_kv_create_val()` builds the persistent client value `<client_addr>-(len:client-string)`.
- `rados_kv_put()`, `rados_kv_get()`, `rados_kv_del()`, and `rados_kv_traverse()` perform omap mutation, lookup, deletion, and paged traversal.
- `rados_kv_connect()` creates/configures/connects a librados client, creates the pool if needed, creates an ioctx, and sets namespace.
- `set_nodeid()` chooses `nodeid` from `g_nodeid`, config `nodeid`, or hostname, prepending `node` for numeric ids.
- `rados_kv_init()` creates current `<nodeid>_recov` and old `<nodeid>_old` objects and installs refcounted object names.
- `rados_kv_add_clid_impl()`/`rados_kv_rm_clid_impl()` implement object-specific add/remove, with public wrappers using current object.
- `rados_kv_pop_clid_entry()` parses values, imports revoked file handles, moves current entries to old during recovery, and deletes processed records when not takeover.
- `rados_kv_read_recov_clids_takeover()` handles normal recovery and IP takeover object traversal.
- `rados_kv_cleanup_old()` clears the old object at end grace.
- `rados_kv_add_revoke_fh()` reads a client value, appends `#<base64url-fh>`, and writes it back.

## Control flow

Initialization sets node identity, builds current and old object names, connects to Ceph, and creates both objects if absent. Add/remove operations use `rados_kv_create_key()` to map the numeric `cid_clientid` to a decimal key and store the generated value in the current object.

Normal recovery reads old first with `old=true`, then current with `old=false`. Each omap entry is parsed into a client reclaim entry; non-old entries are copied into the old object before deletion from current. This mirrors the legacy filesystem current-to-old recovery epoch behavior.

Takeover builds an object name from `gsp->ipaddr` plus `_recov` and traverses it with `takeover=true`, which imports entries without deleting them. End grace clears old object omap state.

Revoked delegation persistence is value-based: the backend reads the existing value, appends a `#` separator and base64url file handle, and writes the full value back.

## State and persistence behavior

The persistent model is RADOS object omap. Keys are decimal client IDs. Values are NUL-terminated strings containing client identity and optional revoked file-handle fragments separated by `#`. Current and old objects implement crash recovery across grace epochs.

RADOS object-name pointers are `gsh_refstr` values published through RCU. `rados_kv_shutdown()` destroys the ioctx/client and swaps out `rados_recov_oid`, but `rados_recov_old_oid` is not explicitly swapped in shutdown in this file, so lifetime review should include all backend combinations.

## Dependencies and integration points

The file depends on librados, `rados_grace.h` for defaults, `bsd-base64`, config parsing, client manager types, RCU, and generic recovery hooks. Other backends call its config, connection, traversal, node-id, value, and revoked-handle helpers.

## Risks and edge cases

- `rados_kv_get()` copies `val_len_out + 1` into caller storage without a size argument, relying on internal `RADOS_VAL_MAX_LEN` discipline.
- `rados_kv_append_val_rdfh()` uses `strncat()` with remaining buffer calculations but does not explicitly report truncation when too many revoked handles accumulate.
- `rados_kv_pop_clid_entry()` calls `strtok(rfh_names, "#")` even when `rfh_names` can be `NULL`, which is safe for `strtok(NULL, ...)` continuation semantics only if a previous tokenization state is suitable; this deserves scrutiny because it intends to parse an optional second token.
- `set_nodeid()` allocates `nodeid` each call and some error paths do not free it locally.
- Pool creation during connect may be inappropriate for deployments where the pool must be pre-created with specific settings.
- Takeover is limited to IP-derived object naming in this backend.

## Test signals

Tests should cover config parsing, node-id selection, object creation, add/remove/get traversal, old/current recovery movement, takeover traversal, revoked-handle append and import, values at `PATH_MAX`, missing keys, RADOS operation failures, namespaces, and shutdown lifetime. Fuzz tests for value parsing should include no `#`, one revoked handle, multiple handles, empty values, and malformed client strings.
