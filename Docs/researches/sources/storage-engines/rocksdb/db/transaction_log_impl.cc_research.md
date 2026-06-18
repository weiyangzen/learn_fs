# sources/storage-engines/rocksdb/db/transaction_log_impl.cc

## Purpose

`transaction_log_impl.cc` implements `TransactionLogIteratorImpl`, the public WAL iterator used to stream write batches from archived and live log files starting at a requested sequence number while enforcing sequence continuity.

## Important APIs, Types, and Functions

Implemented methods include the constructor, `OpenLogFile`, `GetBatch`, `status`, `Valid`, `RestrictedRead`, `SeekToStartSequence`, `Next`, `NextImpl`, `IsBatchExpected`, `UpdateCurrentWriteBatch`, and `OpenLogReader`. It uses `WriteBatchInternal` to parse batch contents, sequence, and count.

## Control Flow

Construction initializes reporter state and immediately seeks to the requested sequence. `OpenLogFile` tries the expected live or archive path, falling back from live to archive if needed. `SeekToStartSequence` scans records until the current batch covers the requested sequence, optionally requiring exact alignment in strict mode. `NextImpl` reads records from the current log, advances files on EOF, and returns `TryAgain` at the live tail when DB last sequence has advanced beyond what was read. If a batch sequence is not the expected next sequence after iteration has started, `UpdateCurrentWriteBatch` logs the discontinuity, rewinds to a previous file if needed, updates the target sequence, and reseeks.

## State and Persistence Behavior

The iterator owns current `WriteBatch`, `log::Reader`, scratch buffer, file index, current batch start sequence, and current last sequence. It does not write WAL data. `RestrictedRead` refuses to read past `VersionSet::LastSequence`, so the iterator does not expose incomplete future tail records.

## Dependencies and Integration Points

Dependencies include `log_reader`, `VersionSet`, filename helpers, filesystem sequential readers, immutable DB options, IO tracing, write batch internals, and logging. DB APIs that expose transaction logs construct this iterator with WAL metadata collected from live/archive logs.

## Risks and Test Signals

Risks include sequence gaps across rolled logs, WAL files moving to archive while opening, ignoring `SetContents` parse errors, off-by-one batch coverage for requested sequence inside a batch, and `TryAgain` behavior at live tail. Tests should cover archived fallback, missing first sequence strict/non-strict modes, very small/corrupt records, multi-file iteration, sequence discontinuity reseek, checksum verification, and no read beyond last sequence.
