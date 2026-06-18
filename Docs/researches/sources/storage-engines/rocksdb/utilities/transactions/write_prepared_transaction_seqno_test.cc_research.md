# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_transaction_seqno_test.cc

## Purpose
This file is a regression test suite for write-prepared `TransactionDB` sequence-number consistency during retryable background error recovery with `two_write_queues=true`. It verifies the fix that calls `SyncLastSequenceWithAllocated()` during `DBImpl::ResumeImpl`, preventing later recovery from seeing sequence numbers go backwards after allocated but unpublished sequence numbers exist.

## Important APIs, Types, and Functions
`WritePreparedTransactionSeqnoTest` is a GoogleTest fixture that owns a write-prepared `TransactionDB`, `SpecialEnv`, `FaultInjectionTestFS`, composite environment, DB path, `Options`, `TransactionDBOptions`, and optional column-family handles. The constructor enables `two_write_queues`, small memtables, retryable background-error auto recovery (`max_bgerror_resume_count = 2`, `bgerror_resume_retry_interval = 100ms`), and write-prepared policy. `Open()` calls `TransactionDB::Open()`, `Close()` destroys handles and deletes the DB, and `dbimpl()` casts the root DB to `DBImpl`.

The test cases are `SeqnoGoesBackwardsDuringErrorRecovery`, `SeqnoDiscrepancyDuringErrorRecovery`, and `ConcurrentWritesDuringErrorRecovery`. They use `FaultInjectionTestFS` to disable the filesystem with a retryable `IOStatus`, `SyncPoint` dependencies and callbacks to make recovery deterministic, `VersionSet::LastSequence()`, `VersionSet::LastAllocatedSequence()`, and DBImpl sync points such as `DBImpl::ResumeImpl:Start` and `DBImpl::ResumeImpl:AfterSyncSeq`.

## Control Flow
Each test opens the DB, writes initial prepared transactions, flushes to establish a baseline, then writes more prepared transactions before installing error injection. A callback on `VersionSet::LogAndApply:WriteManifest` disables the filesystem so a subsequent flush fails with a retryable MANIFEST write error. Sync-point dependencies wait for `RecoverFromRetryableBGIOError:BeforeStart`, then the test clears the fault callback, re-enables the filesystem, lets recovery proceed past `BeforeWait1`, and waits for `RecoverSuccess`.

`SeqnoGoesBackwardsDuringErrorRecovery` writes additional transactions after recovery, closes, reopens, and verifies all original data can be read; before the fix, reopen could fail with sequence-number corruption. `SeqnoDiscrepancyDuringErrorRecovery` captures `LastSequence` and `LastAllocatedSequence` at recovery success and asserts `LastSequence >= LastAllocatedSequence`, then reopens and checks data. `ConcurrentWritesDuringErrorRecovery` captures sequence numbers at `ResumeImpl` start and after `AfterSyncSeq`, asserts the after-sync callback fired and the two values are equal, then reopens and verifies data.

## State and Persistence Behavior
The tests persist prepared transaction writes, WAL records, memtable flush state, and MANIFEST updates under a fault-injectable filesystem. The key state under examination is not user data alone but `VersionSet` sequence bookkeeping: allocated sequence numbers from two write queues must be synchronized with published last sequence during recovery before new memtables or WALs can make the apparent sequence order regress. Retryable background-error recovery mutates DB state asynchronously, so sync points pin the exact recovery window.

## Dependencies and Integration Points
The suite integrates transaction DB write-prepared behavior, two write queues, `DBImpl` background error recovery, `VersionSet` sequence allocation, MANIFEST write path, fault-injection filesystem, sync-point test framework, and RocksDB's test harness. It depends on recovery sync-point names remaining stable and on `FaultInjectionTestFS::SetFilesystemActive()` producing retryable flush failure and later successful recovery.

## Risks and Edge Cases
These tests are timing-sensitive by nature, so deterministic sync-point dependencies are essential. The error-injection callback must be cleared before reenabling the filesystem or recovery itself can immediately re-disable writes. Small write buffers can trigger automatic flushes, so tests write all pre-fault transactions before installing the fault callback. The fixture destructor clears sync points globally, which is necessary to prevent callbacks leaking across tests. Assertions focus on sequence synchronization and successful reopen, not exhaustive validation of every recovery side effect.

## Test Signals
A passing run signals that retryable MANIFEST failures followed by auto recovery no longer leave `LastSequence` behind `LastAllocatedSequence` in write-prepared two-write-queue mode. It also confirms post-recovery writes, clean close/reopen, and user data reads remain valid after the recovery sequence.
