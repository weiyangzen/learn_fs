# sources/object-store/garage/src/db/Cargo.toml

Purpose: declares the `garage_db` crate, a transactional key/value abstraction over multiple embedded storage engines.

Important APIs/types/functions: configures `lib.rs`; features `default = ["lmdb", "sqlite"]`, `bundled-libs`, `lmdb`, `fjall`, and `sqlite`; optional dependencies for `heed`, `rusqlite`, `r2d2`, `r2d2_sqlite`, `fjall`, and `parking_lot`.

Control flow: Cargo feature resolution determines which adapters compile and which `Engine` values can be opened at runtime.

State and persistence: build-time feature choices select supported metadata DB formats. `bundled-libs` affects SQLite library linkage.

Dependencies and integration points: used by `garage`, `garage_model`, and block/table components. Development tests use `mktemp`.

Risks: disabling a feature makes that engine unavailable even though `Engine` still parses the name. Adapter dependency upgrades can affect locking, transaction behavior, snapshot semantics, and file format compatibility.

Test signals: crate tests in `test.rs` run per enabled feature and are the main cross-engine conformance signal.
