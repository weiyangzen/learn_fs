# sources/object-store/rustfs/crates/ecstore/src/config/com.rs

## Purpose
This file is the ecstore server-config persistence and migration layer. It reads and writes metadata-bucket config objects, translates between RustFS internal `Config`/`KVS` maps and the external MinIO-style JSON object shape, migrates compatible legacy config from the migrating metadata bucket, and applies dynamic runtime config such as storage-class parity to globals.

## Important APIs, types, and functions
Important public APIs are `read_config`, `read_config_no_lock`, `read_config_with_metadata`, `save_config`, `delete_config`, `save_config_with_opts`, `try_migrate_server_config`, `read_config_without_migrate`, `save_server_config`, and `lookup_configs`. `TargetConfigDescriptor` maps external notify/audit target groups onto subsystem keys, defaults, and valid key lists. Helpers decode and encode storageclass, OIDC, notify, and audit shapes, compare semantic equality, and detect standard object-server config.

## Control flow
Reads use object-layer `get_object_reader` against `RUSTFS_META_BUCKET`, map not-found variants to `ConfigNotFound`, and reject empty bodies. `read_config_without_migrate` loads `config/config.json`, initializes missing config through the first local cluster node, and merges defaults. `try_migrate_server_config` refuses to overwrite an existing config, reads legacy data from `MIGRATING_META_BUCKET`, decodes compatible data, normalizes it to external object JSON, and saves it. Saves preserve existing unknown top-level JSON where possible and skip writes when current persisted semantics already match.

## State and persistence behavior
The persistent object is `config/config.json` in `RUSTFS_META_BUCKET`; generic saves use max parity. The encoder writes external JSON keys such as `storageclass`, `openid`, `notify`, and `logger`, not raw internal subsystem aliases. Runtime dynamic state is copied into `GLOBAL_STORAGE_CLASS` through `set_global_storage_class`.

## Dependencies and integration points
It depends on `ObjectIO`, `ObjectOperations`, `StorageAdminApi`, object metadata options, metadata bucket constants, `rustfs_config` subsystem constants/defaults, and cluster-node role detection. `config/mod.rs` calls it during startup and default installation. Admin config, storage-class lookup, OIDC, notification, and audit runtime setup all depend on these persisted shapes.

## Risks and edge cases
The conversion logic is a compatibility boundary: changing key aliases, boolean normalization, hidden-empty handling, default merging, or target instance detection can drop config. Save idempotency currently compares storageclass, OIDC, notify, and audit only, so future subsystems need explicit semantic comparison. Migration is best-effort and can silently skip bad legacy config after logging. Encrypted config has a TODO in the reload path.

## Test signals
Tests cover internal/external decode shapes, legacy `hiddenIfEmpty`, storageclass round trips, OIDC conversion, notify/audit target decode and encode, shorthand targets, semantic equality, standard object-shape detection, and a distributed-lock read with one unhealthy locker. They do not cover actual migration, encrypted config, or multi-node persistence races.
