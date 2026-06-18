# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_factory.h

Purpose: declares cuckoo table hashing and the `CuckooTableFactory` used to create cuckoo table readers/builders.

Important APIs/types/functions: `CuckooHash` computes a candidate bucket from a user key, hash index, hash mode, table size, identity-first setting, and optional test hash callback. `CuckooTableFactory` implements `Name`, `NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, and `Clone`.

Control flow: `CuckooHash` optionally delegates to a test callback in debug/Windows builds. Otherwise it uses identity hash for hash 0 when configured, or MurmurHash seeded by `kCuckooMurmurSeedMultiplier * hash_cnt`. It maps to a bucket with modulo or power-of-two masking depending on `use_module_hash`.

State and persistence: factory state is `CuckooTableOptions`. Hash choices and options flow into persisted table properties through the builder and must match reader lookup behavior.

Dependencies/integration: derives from `TableFactory`, uses public RocksDB options/table APIs, and includes MurmurHash. Comments document major format limitations: fixed key/value lengths, no snapshots, no merge operations, and no prefix bloom filters.

Risks and test signals: identity hashing reinterpret-casts key bytes as `int64_t`, which assumes sufficient key size and alignment tolerance. Power-of-two masking requires table sizes to be powers of two. Tests in `cuckoo_table_builder_test.cc` use the debug hash callback to make placement deterministic, but production hash behavior needs reader/table tests outside this subset.
