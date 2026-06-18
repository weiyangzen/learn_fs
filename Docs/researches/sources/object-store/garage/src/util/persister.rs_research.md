<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/persister.rs -->
# sources/object-store/garage/src/util/persister.rs

## Purpose
Synchronous/asynchronous file persistence helpers for migration-aware Garage values, plus an in-memory shared wrapper that saves changes.

## Important APIs, types, and functions
`Persister<T>` exposes `new`, `load`, `save`, `load_async`, and `save_async`; private `decode` logs a hexdump on migration failure. `PersisterShared<V>` wraps a `Persister` and `RwLock<V>` with `new`, `get_with`, and `set_with`.

## Control flow
Loads read the full file, decode via `T::decode`, and return structured errors on failure. Saves encode and truncate/create the file. `PersisterShared::new` loads existing state or defaults; `set_with` mutates under a write lock then saves.

## State and persistence behavior
This module writes durable local files but does not fsync or use atomic rename. Failed saves after in-memory mutation can leave memory and disk inconsistent for that call.

## Dependencies and integration points
Used for local node settings and background variables. Depends on `Migrate`, Garage errors, std and Tokio file IO, locks, and tracing macros.

## Risks and test signals
Truncate-in-place risks partial files on crash. Tests should cover missing file defaults, decode failure, save/load round-trip, async variants, and `PersisterShared` mutation persistence.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/persister.rs -->
