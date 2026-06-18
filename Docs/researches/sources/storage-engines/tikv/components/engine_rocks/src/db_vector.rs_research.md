<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/db_vector.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/db_vector.rs

Purpose: adapts `rocksdb::DBVector` to the engine abstraction's owned byte-vector trait.

Important APIs/types/functions: `RocksDbVector`, `from_raw`, `DbVector` impl, `Deref<Target=[u8]>`, `Debug`, and `PartialEq<&[u8]>`.

Control flow: values returned by RocksDB reads are wrapped with `from_raw`; callers dereference to bytes without copying. Debug formatting delegates to the byte slice.

State and persistence behavior: the wrapper owns the read value materialized by RocksDB. It does not persist state and has no mutation behavior.

Dependencies/integration: used by `RocksEngine` `Peekable` methods as `type DbVector`; depends on `engine_traits::DbVector` and `rocksdb::DBVector`.

Risks: equality is implemented for `&[u8]` only, so other comparisons rely on deref coercion. Debug output dumps raw bytes, which may be verbose or sensitive in logs.

Test signals: no direct tests; read/get tests in `engine.rs` validate behavior through dereferencing and equality checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/db_vector.rs -->
