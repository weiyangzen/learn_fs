# sources/storage-engines/leveldb/include/leveldb/options.h

Purpose: declares configuration structures for database, read, and write operations.

Important APIs and types: `CompressionType` values `kNoCompression`, `kSnappyCompression`, `kZstdCompression`; `Options` fields for comparator, creation flags, paranoid checks, env, info log, write buffer, open-file limit, block cache/size/restart interval, max file size, compression, zstd level, log reuse, and filter policy; `ReadOptions` fields `verify_checksums`, `fill_cache`, `snapshot`; `WriteOptions::sync`.

Control flow: `Options` is supplied at DB/table-builder open time, while `ReadOptions` and `WriteOptions` alter individual operations. Some table builder options can change dynamically.

State and persistence behavior: comparator name/order, compression type, table block layout choices, filter policy name/encoding, and write sync semantics affect persistent data. `reuse_logs` affects recovery/open behavior. Larger write buffers lengthen recovery work.

Dependencies and integration: references comparator, env, cache, filter policy, logger, and snapshot APIs. Used by DB, table, table builder, repair, and cache code.

Risks and edge cases: compression enum values are persistent and must not change. Opening an existing DB with a different comparator is invalid. `sync=false` can lose recent writes on machine crash. `filter_policy` must remain live while DB is open.

Test signals: recovery tests cover `reuse_logs`; issue178 disables compression to stabilize compaction layout; memenv DB tests set `env`.
