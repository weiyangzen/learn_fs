# sources/storage-engines/rocksdb/db/write_batch_internal.h

Purpose: This internal header exposes RocksDB-private controls for manipulating `WriteBatch` serialized contents, column-family memtable lookup, memtable insertion, timestamp updates, transaction markers, append, and protection information.

Important APIs/types/functions: `ColumnFamilyMemTables` is the abstract lookup interface used during insertion, with `ColumnFamilyMemTablesDefault` for default-CF-only insertion. `WriteBatch::ProtectionInfo` stores `ProtectionInfoKVOC64` entries. `WriteBatchInternal` declares internal mutation APIs by column-family ID, transaction marker helpers, header accessors (`Count`, `SetCount`, `Sequence`, `SetSequence`), `Contents`, `ByteSize`, `SetContents`, `InsertInto` overloads, `Append`, `Iterate`, timestamp flags, and `UpdateProtectionInfo`. `LocalSavePoint` is an RAII rollback helper. `TimestampUpdater` is a templated `WriteBatch::Handler` for in-place timestamp replacement.

Control flow: Public `WriteBatch` APIs resolve handles to CF IDs and timestamp sizes, then call `WriteBatchInternal` methods. Insertion overloads route a single batch, writer, or write group into memtables. `LocalSavePoint::commit()` checks `max_bytes_` and rolls back serialized bytes, count, protection entries, and flags on memory-limit failure. `TimestampUpdater` iterates records and rewrites trailing timestamp bytes based on a supplied CF-to-size function.

State and persistence behavior: The header defines the 12-byte batch header contract and grants access to private `WriteBatch` fields. Protection info is a parallel per-counted-write structure and must match `Count()`. Timestamp updates mutate serialized keys in place and update protection info when present.

Dependencies and integration points: It includes flush and trim schedulers, write thread, RocksDB DB/options/types/write batch APIs, checksum utilities, `autovector`, and cast helpers. It is consumed by `write_batch.cc`, DB write/recovery paths, tests, transactions, and write-batch-with-index code.

Risks: These APIs bypass public invariants and must keep serialized bytes, count, content flags, timestamp metadata, and protection info synchronized. `TimestampUpdater` returns `NotFound` for unknown CF timestamp sizes and `InvalidArgument` for size mismatches. `LocalSavePoint` asserts commit in debug builds, so internal mutators must call `commit()`.

Test signals: Write-batch tests directly exercise header accessors, append, internal markers, serialized V2 entity preservation, timestamps, savepoints, and insertion into test memtables.
