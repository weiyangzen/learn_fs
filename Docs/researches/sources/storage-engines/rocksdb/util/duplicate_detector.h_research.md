# sources/storage-engines/rocksdb/util/duplicate_detector.h

Purpose: recovery-time helper that emulates memtable duplicate key/sequence detection when a memtable flush prevents normal insertion-based duplicate detection.

Important type/API: `DuplicateDetector` owns a `DBImpl*`, current `batch_seq_`, and a map from column family id to `std::set<Slice, SetComparator>`. `IsDuplicateKeySeq(cf, key, seq)` returns true when the same key appears twice for the same sequence batch.

Control flow: asserts `seq >= batch_seq_`; a new sequence clears all tracked keys. For each column family, it lazily initializes the set comparator from the DB column family handle. On duplicate insertion, it clears/reinitializes tracking for that CF, reinserts the key, and reports true.

State and persistence: in-memory per-recovery-batch state only. It stores `Slice` objects, so key memory lifetime must exceed tracking use.

Dependencies and integration: depends on `DBImpl`, logging, `SetComparator`, column family handles, sequence numbers, and RocksDB logging/status conventions. It is intended for WAL recovery logic.

Risks: dropped column family during recovery logs fatal and throws. Slice lifetime is critical. The class is not thread-safe. Clearing all keys on new batch assumes sequence changes exactly delimit duplicate-detection windows.

Test signals: no direct test in this subset.
