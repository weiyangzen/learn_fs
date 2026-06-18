## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_test.cc`

Purpose: comprehensive unit and integration tests for legacy BlobDB behavior. The file validates basic API semantics, blob index encoding, TTL expiration, I/O failure handling, file lifecycle, snapshot protection, user compaction filters, garbage collection, live-file metadata, and unsupported surfaces.

Important APIs and helpers: `BlobDBTest` owns temporary DB paths, mock and fault-injection envs, `TryOpen`, `Open`, `Reopen`, `Close`, `Destroy`, typed access to `BlobDBImpl`, write/delete helpers, random value helpers, `VerifyDB`, `VerifyBaseDB`, `VerifyBaseDBBlobIndex`, and `InsertBlobs`. `BlobIndexVersion` describes expected base DB blob-index metadata for verification.

Control flow: individual tests open BlobDB with targeted `BlobDBOptions` and RocksDB `Options`, write values through `Put`, `PutWithTTL`, or `WriteBatch`, sometimes force blob file closure via `TEST_CloseBlobFile`, then verify both user-visible DB output and base DB internal versions. Tests use mock time to make TTL deterministic, fault-injection envs and sync points to induce I/O failures, and manual compaction/flush helpers to trigger compaction filters and GC.

State and persistence behavior: tests inspect blob file number allocation, footer closure, expiration ranges, live immutable non-TTL sets, obsolete lists, SST link sets, deletion disable counters, live-file metadata, and statistics counters. Restart tests verify trash cleanup and migration from plain RocksDB to BlobDB. Snapshot tests verify obsolete files remain physically present until snapshots that might see old blob indexes are released.

Dependencies and integration: pulls in BlobDB public API, `BlobDBImpl` debug hooks, `BlobIndex`, `DBTestUtil` helpers, `SstFileManagerImpl`, `MockSystemClock`, `FaultInjectionTestEnv`, `SyncPoint`, `Random`, and RocksDB compaction/filter APIs. It uses the base DB directly for internal verification.

Risks covered: unsupported non-default column family operations, snapshot races during GC deletion, I/O failures during get/put/compaction close/write, expired index filtering despite snapshots, missing blob-file indexes, max DB size limit returning no-space I/O status, concurrent writers, shutdown while background eviction is running, and user compaction filters modifying or dropping blob values.

Test signal summary: this is the primary regression suite for `utilities/blob_db`. It covers broad behavior but is oriented around deterministic unit setups; performance, crash-recovery windows between blob append and base DB write, and multi-CF support remain outside the intended contract.
