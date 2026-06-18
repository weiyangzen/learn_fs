# sources/storage-engines/rocksdb/rocksdb.pc.in

Purpose: CMake/pkg-config template for installed RocksDB metadata.

Important APIs/types/functions: pkg-config fields `prefix`, `includedir`, `libdir`, `Name`, `Description`, `URL`, `Version`, `Cflags`, and `Libs`.

Control flow: CMake substitutes `@...@` variables during installation to produce `rocksdb.pc`.

State and persistence behavior: persists install metadata used by downstream builds; it does not affect runtime state.

Dependencies and integration points: consumed by `pkg-config` clients compiling/linking against installed RocksDB.

Risks and test signals: missing private dependency libs may affect static linking consumers. Install/package tests and downstream compile checks are useful.
