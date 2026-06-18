# sources/user-network-fs/samba/source3/registry/reg_backend_db.c

## Purpose

`reg_backend_db.c` is the default persistent backend for Samba’s virtual registry. It stores key subkey lists, key values, and key security descriptors in `registry.tdb`; initializes built-in registry paths and default values; upgrades old DB formats; exposes transaction/open/close utilities; and publishes a `registry_ops` table used by the high-level registry API.

## Important APIs, Types, and Functions

- Global `regdb` and `regdb_refcount` manage the shared DB context.
- `regdb_trans_do()` wraps actions in a DB transaction and rejects writes if the stored DB version no longer equals `REGDB_CODE_VERSION`.
- `init_registry_key()` and `init_registry_data()` create built-in paths/values.
- `regdb_init()`, `regdb_open()`, `regdb_close()`, transaction wrappers, and `regdb_get_seqnum()` manage DB lifecycle.
- Upgrade helpers normalize slash paths and migrate v2 to v3 by creating missing subkey-list records and deleting sorted subkey caches.
- Key helpers include `regdb_key_exists()`, `regdb_fetch_keys_internal()`, `regdb_store_keys_internal()`, `regdb_create_subkey_internal()`, `regdb_delete_subkey()`, and `regdb_delete_key_lists()`.
- Value helpers include `regdb_fetch_values_internal()`, `regdb_pack_values()`, `regdb_unpack_values()`, and `regdb_store_values_internal()`.
- Security helpers `regdb_get_secdesc()` and `regdb_set_secdesc()` marshal/unmarshal security descriptors.
- `regdb_ops` exports backend operations to the registry dispatcher.

## Control Flow

Initialization opens `state_path("registry.tdb")`, creating it with mode `0600` if necessary and storing the current version. Existing DBs are version-checked; missing version records are treated as v1, unknown/future versions are rejected, and upgrades run inside one transaction. Built-in initialization first checks for missing paths/values to avoid unnecessary writes, then creates all configured built-in path components and default values inside one transaction.

Keys are represented by a normalized key-name record containing a packed count and zero-terminated subkey names. Key existence is defined by a structurally valid subkey-list record. Creating a subkey transactionally fetches the parent list, adds the subkey, stores the parent list, and creates an empty child subkey-list record. Storing subkey lists deletes removed children’s value/security/subkey records before replacing the parent list, then creates records for new children. Deleting a subkey removes value, security, and subkey-list records and optionally removes the child from the parent list.

Values are stored under `REG_VALUE_PREFIX\key` as a packed count plus `name,type,size,data` tuples. Fetching values checks key existence, reads with stable seqnum retry, and unpacks into a `regval_ctr`. Storing values deletes the value record when the container is empty; otherwise it avoids writes if packed data is unchanged and uses transactional store. Security descriptors are stored under `REG_SECDESC_PREFIX\key` using Samba security descriptor marshal helpers.

## State and Persistence

Persistent state is a dbwrap/TDB database at `state_path("registry.tdb")`. Logical namespaces are the raw normalized key path for subkey lists, `REG_VALUE_PREFIX\...` for values, `REG_SECDESC_PREFIX\...` for security descriptors, and `INFO/version` for DB version. In-memory state is the singleton DB context and refcount.

## Dependencies and Integration Points

The backend depends on dbwrap open/store/fetch/traverse/transaction APIs, TDB pack/unpack helpers, registry container objects, registry path normalization, hive metadata, built-in key macros, NT printing key constants, security descriptor marshal/unmarshal, and loadparm clustering checks. `reg_api.c` and registry dispatchers call the exported `regdb_ops` and lifecycle functions.

## Risks and Edge Cases

- DB corruption is detected by subkey-list structural checks; corrupt keys become non-existent and can block operations.
- Raw packed formats are compatibility-sensitive and must preserve endianness/string assumptions.
- Stable reads use seqnum retry loops; heavy concurrent writers can cause repeated fetch attempts.
- Upgrade v2-to-v3 logs inconsistencies and asks for `net registry check` but may continue past some malformed records.
- `regdb_trans_do()` prevents writes during version mismatch, but direct helpers must be routed through it for safety.
- Clustering requires root unless uid wrapper is enabled.

## Test Signals

Tests should cover fresh DB creation, refcounted open/close, version-missing and version-upgrade paths, future-version rejection, built-in path/value idempotence, create/delete subkeys, removed-child data purging, empty value deletion, unchanged value no-op, corrupt subkey/value records, secdesc marshal failures, seqnum cache invalidation, and transaction rollback on injected store failures.
