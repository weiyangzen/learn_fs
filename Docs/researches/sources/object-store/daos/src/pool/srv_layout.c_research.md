# sources/object-store/daos/src/pool/srv_layout.c

## Purpose

This file defines the RDB key objects and default pool property values for the DAOS pool server persistent metadata layout. It instantiates the keys declared by `srv_layout.h` and initializes dynamically allocated defaults.

## Important APIs, types, and functions

- `RDB_STRING_KEY(ds_pool_prop_, ...)` and `RDB_STRING_KEY(ds_pool_attr_, user)`: instantiate persistent key names.
- `pool_prop_entries_default[DAOS_PROP_PO_NUM]`: full default table for optional pool properties.
- `pool_prop_default`: `daos_prop_t` view over the default table.
- `ds_pool_prop_default_init()`: allocates the default DAOS pool ACL.
- `ds_pool_prop_default_fini()`: frees the dynamic default ACL.

## Control flow

RDB key symbols are created at load time by macros. During pool module initialization, `srv.c` calls `ds_pool_prop_default_init()`, which finds the ACL property and fills it with `ds_sec_alloc_default_daos_pool_acl()`. Finalization frees the ACL pointer.

## State and persistence behavior

The file defines key symbols used by service RDB transactions but does not transact directly. The default property table is process-global state. Persistent layout includes root pool properties, pool handles, user attributes, service-op tracking, server handles, and recovery-container markers.

## Dependencies and integration points

It depends on RDB helpers, security default ACL allocation, and DAOS property constants. `srv_pool.c` uses the keys for create/load/update/query/upgrade. `srv_iv.c` mirrors the property set in `struct pool_iv_prop`. `srv_layout.h` documents the shared root KVS namespace constraints.

## Risks and test signals

The default entries must stay aligned with `DAOS_PROP_PO_NUM`. New properties require updates across defaults, layout declarations, RDB code, IV serialization, set/query validation, and tests. Tests should cover ACL allocation failure, exact default coverage, expected key names, default persistence on pool create, and add-property guard failures.
