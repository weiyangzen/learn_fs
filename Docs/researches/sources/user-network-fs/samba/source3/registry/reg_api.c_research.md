# sources/user-network-fs/samba/source3/registry/reg_api.c

## Purpose

`reg_api.c` implements a winreg-like high-level API over Samba’s virtual registry layer. It opens hives and subkeys, enforces access masks, caches subkeys and values, enumerates and queries data, creates/deletes keys, sets/deletes values, manages security descriptors, reports registry version, and provides recursive deletion utilities.

## Important APIs, Types, and Functions

- `fill_value_cache()` and `fill_subkey_cache()` refresh `registry_key` caches when backend sequence numbers indicate stale data.
- `regkey_open_onelevel()` allocates a `registry_key`, opens `registry.tdb`, resolves backend hooks, verifies existence by fetching subkeys, and applies `regkey_access_check()`.
- `reg_openhive()` and `reg_openkey()` open hive roots or multi-component paths.
- `reg_enumkey()`, `reg_enumvalue()`, `reg_queryvalue()`, `reg_querymultiplevalues()`, and `reg_queryinfokey()` implement read/query operations.
- `reg_createkey()` creates one or more path components under a transaction and reports opened-vs-created action.
- `reg_deletekey()`, `reg_deletekey_recursive()`, and `reg_deletesubkeys_recursive()` delete keys with transaction handling.
- `reg_setvalue()`, `reg_deletevalue()`, and `reg_deleteallvalues()` mutate value containers.
- `reg_getkeysecurity()` and `reg_setkeysecurity()` delegate security descriptor access.
- `reg_getversion()` returns Windows 2000-compatible version `0x00000005`.

## Control Flow

Opening a key starts with a hive lookup or parent key. `reg_openkey()` splits multi-component paths, opening intermediate components with enumerate access, then opens the final component with requested access. `regkey_open_onelevel()` allocates the key object and handle, duplicates the security token, opens the registry DB with destructor-backed refcounting, marks HKPD performance keys, selects backend ops through `reghook_cache_find()`, fills subkeys to prove existence, and checks access.

Read operations check the access bits stored in the key handle before refreshing caches. Enumeration returns `WERR_NO_MORE_ITEMS` when the requested index exceeds the cached container. Query-by-name scans the existing cache and uses the no-cache-fill enum helper to avoid changing indexes mid-query. Query-info computes max key/value sizes and obtains the security descriptor size via NDR.

Mutation operations are transaction-oriented. `reg_createkey()` starts a DB transaction, recursively creates intermediate path components if needed, checks `KEY_CREATE_SUB_KEY`, calls backend `create_reg_subkey()`, opens the new key, and commits or cancels. `reg_setvalue()` and `reg_deletevalue()` fill the value cache, adjust the container, call `store_reg_values()`, and commit/cancel. `reg_deletekey()` refuses keys with subkeys, while recursive deletion walks children from the end of the subkey list and deletes bottom-up.

## State and Persistence

State is represented by `struct registry_key`, its `registry_key_handle`, cached `regsubkey_ctr` and `regval_ctr` containers, duplicated security token, backend ops pointer, granted access mask, and backend-specific persistent data. Persistent storage is usually `registry.tdb` through `reg_backend_db.c`, but hook backends can overlay virtual values/subkeys. `regkey_destructor()` closes the registry DB reference when the key handle is freed.

## Dependencies and Integration Points

The file depends on registry core types, hook cache lookup, backend DB open/transaction APIs, dispatcher helpers (`fetch_reg_keys`, `store_reg_values`, `create_reg_subkey`, etc.), security token duplication, access-check helpers, NDR security descriptor sizing, and regval/regsubkey containers. It is the core API consumed by RPC winreg handlers and registry utilities.

## Risks and Edge Cases

- Caches rely on backend sequence numbers; a backend with weak `*_need_update` semantics can return stale data.
- `reg_querymultiplevalues()` counts found values but stores each result at the requested-name index, so callers must understand sparse semantics.
- Recursive `reg_createkey()` starts transactions recursively; this relies on underlying transaction nesting behavior.
- Access checks happen at open and before operations; callers retaining handles across policy changes may have stale granted access.
- `reg_deleteallvalues()` deletes while iterating forward over a changing container, which deserves regression coverage.

## Test Signals

Tests should cover hive open failures, path normalization with trailing separators, access denial for missing query/set/create rights, cache refresh on sequence number changes, create existing vs new action, transaction rollback on failed create/set/delete, non-recursive delete refusal for keys with subkeys, recursive deletion order, security descriptor query sizing, and multi-value query behavior.
