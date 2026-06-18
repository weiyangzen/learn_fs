# Research: sources/storage-engines/rocksdb/include/rocksdb/transaction_log.h

- **Purpose:** Exposes WAL metadata and transaction-log iteration APIs for reading write batches from RocksDB logs.
- **Important APIs/types/functions:** `WalFileType` distinguishes archived and live logs. `WalFile` exposes `PathName()`, `LogNumber()`, `Type()`, `StartSequence()`, and `SizeFileBytes()`. `BatchResult` carries a starting `SequenceNumber` and move-only `WriteBatch`. `TransactionLogIterator` exposes `Valid()`, `Next()`, `status()`, `GetBatch()`, and nested `ReadOptions` with checksum verification.
- **Control flow:** Callers enumerate WAL files through DB APIs or call `GetUpdatesSince()` to obtain a `TransactionLogIterator`. A valid iterator returns batches in sequence until a gap or error; callers use `Next()` only while valid and inspect `status()`.
- **State and persistence:** WAL files are durable DB log files, either live in the DB directory or archived under the archive directory. `StartSequence()` and `BatchResult::sequence` define replay ordering. `SizeFileBytes()` is the flushed extent and matters for recycled WAL files.
- **Dependencies:** Depends on `Status`, `types.h`, and `WriteBatch`.
- **Integration points:** Used by replication, backup, change-data-capture, recovery tooling, and transaction log diagnostics.
- **Risks:** Iteration stops at sequence gaps. Disabling checksum verification trades safety for speed. `BatchResult` is move-only, so API users must not copy it. WAL archival/cleanup options can remove needed history.
- **Test signals:** Tests should cover live/archived file metadata, iterator continuity, gap behavior, checksum verification failures, recycled WAL sizes, and move-only batch ownership.
