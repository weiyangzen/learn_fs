# sources/object-store/daos/src/vos/sys_db.c

## Purpose
Implements the VOS-backed system database used by DAOS server metadata. It stores key/value tables inside a reserved VOS pool/container and exports the generic `struct sys_db` interface.

## Important APIs, types, and functions
- Reserved UUIDs `SYS_DB_POOL` and `SYS_DB_CONT`, directory `daos_sys`, and file name `sys_db`.
- `struct vos_sys_db` wraps public `struct sys_db` with paths, handles, mutex, UUIDs, object id, and umem instance.
- Public functions: `vos_db_init`, `vos_db_init_ex`, `vos_db_fini`, `vos_db_get`, `vos_db_pool_uuid`.
- Interface methods: `db_fetch`, `db_upsert`, `db_delete`, `db_traverse`, `db_tx_begin`, `db_tx_end`, `db_lock`, `db_unlock`.

## Control flow
Initialization builds the sysdb directory/file paths, creates a recursive Argobots mutex, installs method pointers, parses reserved UUIDs, optionally unlinks existing storage, then tries open-first/create-second unless forced. `db_open_create` creates or opens the VOS pool, creates/opens the container, initializes `db_umm`, and writes or validates the metadata version. CRUD methods map table names to dkeys and user keys to akeys in a fixed VOS object at epoch 1.

## State and persistence behavior
Persistent state lives in a 128 MiB VOS pool file under `<db_path>/daos_sys/<db_name>`. Table names are dkeys; keys are akeys; values are single-value IODs. Version metadata is stored in table `metadata`, key `version`. Deletion calls `vos_gc_pool_tight` because `vos_obj_del_key` alone does not free space. `destroy_db_on_fini` controls whether finalization destroys the pool file.

## Dependencies and integration points
Depends on VOS pool/container/object APIs, sys_db headers, UUID parsing, umem transactions, Argobots mutexes, and DAOS error/logging helpers. It is the backing store for DAOS system metadata consumers that call the generic `sys_db` callbacks.

## Risks and edge cases
Failure paths must close partially opened handles and free allocated paths/mutex attributes. Version incompatibility returns `-DER_DF_INCOMPT`. `db_fetch` treats zero-length returned values as nonexistence. Force-create unlinks the file before open/create, so callers must be explicit. The global singleton means concurrent init/fini must be externally controlled.

## Test signals
Signals include create/open idempotence, version read/write and incompatibility handling, correct fetch/upsert/delete/traverse behavior, transaction nesting over umem, mutex recursion, and cleanup with or without pool destruction.
