# sources/object-store/garage/src/db/open.rs

Purpose: provides runtime database engine selection and common open options.

Important APIs/types/functions: `Engine::{Lmdb, Sqlite, Fjall}`, `Engine::as_str`, `Engine::db_path`, `Display`, `FromStr`, `OpenOpt`, and `open_db`.

Control flow: parses engine aliases (`heed` for LMDB, `sqlite3`/`rusqlite` for SQLite), rejects `sled` with migration guidance, and dispatches `open_db` to feature-gated adapter modules. If a valid engine is not compiled in, it returns a clear support-not-available error.

State and persistence: engine-specific paths are `db.lmdb`, `db.sqlite`, and `db.fjall` under a base metadata path. `OpenOpt` carries `fsync`, LMDB map size, and Fjall block-cache size.

Dependencies and integration points: used by Garage startup, local DB conversion CLI, and config parsing paths.

Risks: `Engine` lists all supported engines independent of compile features, so command-line/config validation can succeed and runtime open can still fail. Path conventions are part of migration/conversion tooling.

Test signals: indirectly covered by adapter tests and CLI conversion compile checks.
