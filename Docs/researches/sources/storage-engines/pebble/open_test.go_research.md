# sources/storage-engines/pebble/open_test.go

## Purpose

`open_test.go` is a broad regression and behavior suite for Pebble database opening, closing, file naming, locking, OPTIONS compatibility, read-only mode, WAL replay, WAL corruption detection, WAL failover, crash recovery, consistency checking, and disabled-WAL persistence. The file does not implement production open logic, but it is one of the most important signals for the expected durability and recovery contract around `Open`, `Close`, `GetVersion`, `Peek`, `mkdirAllAndSyncParents`, WAL directory migration, and file-system failure handling.

## Important APIs, Types, and Helpers

- `TestOpenSharedFileCache` verifies that `Options.FileCache` is honored and shared across DB instances when paired with a shared block cache.
- `TestErrorIfExists`, `TestErrorIfNotExists`, and `TestErrorIfNotPristine` cover user-visible open guard options and their error identities: `ErrDBAlreadyExists`, `ErrDBDoesNotExist`, and `ErrDBNotPristine`.
- `TestOpenFormatVersion1NotSupported` asserts that old format-version-1 stores are rejected clearly instead of being treated as empty directories.
- `TestOpen_WALFailover` is datadriven and exercises opening with primary WAL dirs, secondary failover dirs, recovery dirs, identifier files, missing-dir allowances, file listing, stat, and log inspection.
- `TestOpenRecovery` is datadriven and verifies recovery after defining DB state, committing batches, closing, and reopening with changed options.
- `TestOpenAlreadyLocked` covers automatic and caller-provided locks on the data dir, primary WAL dir, secondary WAL dir, and WAL recovery dirs across memfs, disk absolute paths, and disk relative paths.
- `TestNewDBFilenames`, `testOpenCloseOpenClose`, and `TestOpenCloseOpenClose` verify expected newly created file names, repeated open/close persistence, external or store-relative WAL paths, and single live OPTIONS file retention.
- `TestOpenOptionsCheck` and `TestOpenCrashWritingOptions` check persisted OPTIONS compatibility and tolerance of a torn OPTIONS write.
- `optionsTornWriteFS` and `optionsTornWriteFile` simulate a partial write that fails around the serialized `comparer=` field.
- `TestOpenReadOnly` verifies read-only behavior, including non-mutating failed opens, write API failures, iterator/snapshot/indexed-batch reads, and unchanged directory contents.
- WAL replay tests include `TestOpenWALReplay`, `TestWALReplaySequenceNumBug`, `TestOpenWALReplay2`, `TestTwoWALReplayCorrupt`, `TestCrashOpenCrashAfterWALCreation`, `TestOpenWALReplayReadOnlySeqNums`, and `TestOpenWALReplayMemtableGrowth`.
- Crash/corruption randomized tests include `TestWALFailoverRandomized`, `runRandomizedCrashTest`, `TestWALHardCrashRandomized`, `TestWALCorruption`, `TestWALCorruptionBitFlip`, and `TestCrashDuringOpenRandomized`.
- `ensureFilesClosed`, `closeTrackingFS`, and `closeTrackingFile` instrument VFS file handles to catch leaked files in open tests.
- `TestCheckConsistency` builds synthetic `manifest.Version` state and on-disk table files for datadriven consistency checks.
- `TestOpenRatchetsNextFileNum` exercises shared-object storage and next-file-number ratcheting during reopen and open-triggered compactions.
- `TestMkdirAllAndSyncParents`, `TestPeek`, `TestGetVersion`, `TestOpenNeverFlushed`, `TestOpen_ErrorIfUnknownFormatVersion`, and `TestDisableWAL` cover targeted open-adjacent behavior.

## Control Flow and State

Most tests follow the same lifecycle: construct `Options` with a memory, crashable memory, logging, error-injecting, or real filesystem; call `Open`; write keys, flush, compact, ingest, or manipulate DB internals; close; mutate files or crash-clone the filesystem; reopen; then assert either successful state recovery or a specific error. Several tests deliberately inspect or modify internal guarded state under `d.mu`, including `d.mu.compact.flushing`, `d.mu.mem.queue`, `d.mu.versions`, `d.mu.compact.compactingCount`, and file deletion toggles.

The WAL replay tests use value sizes and memtable sizes to force specific replay shapes: one or more WALs, large batches in flushable batches, flushed sstables plus trailing logs, read-only replay without flush-on-open, and manifest sequence numbers ahead of unflushed WAL sequence numbers. The randomized crash runner maintains an expected key-state array with `kvUnset`, `kvMaybeSet`, and `kvSet` so crash clones can validate all recovered keys against conservative durability expectations.

Locking tests pre-acquire different lock combinations and verify that `Open` handles owned locks correctly, rejects concurrent opens on the same data/WAL/secondary directory, and releases references after close. WAL failover tests use datadriven commands to create and reopen stores under evolving primary, secondary, and recovery configurations.

## Persistence and Durability Behavior

This file is heavily focused on persistence. It verifies that:

- Open creates format markers, manifests, OPTIONS files, locks, and WALs with expected names.
- Reopen preserves keys across normal close, read-only replay, WAL-only state, flushed state, ingested-only state, disabled-WAL state after flush, and remote/shared object configurations.
- Corrupted WAL records and bit flips are detected as `ErrCorruption`.
- Strict WAL tail behavior prevents replay past a corrupt earlier WAL when later WALs exist.
- Crash windows during open and immediately after WAL creation remain recoverable.
- Read-only opens do not create or mutate files beyond expected lock handling and keep directory contents unchanged.
- Torn OPTIONS writes do not poison the store because later opens can ignore or recover from incomplete newer OPTIONS files.
- WAL directory changes require appropriate current or recovery directory configuration unless unsafe missing-WAL-dir allowance is explicitly set.

## Dependencies and Integration Points

The tests integrate with `vfs` memory, crashable, logging, default disk, and error-injecting filesystems; `wal` failover and stable identifiers; `atomicfs` marker files; `manifest` versions and table metadata; `objstorageprovider` and `remote` shared storage; `sstable` writers; `datadriven` test fixtures; `metamorphic.Weighted` randomized operation scheduling; `stream` for log slicing; `testkeys`, `testutils`, `leaktest`, `require`, and `pretty` for assertions and diagnostics.

Production integration points under test include `Open`, `DB.Close`, `DB.Set`, `DB.Flush`, `DB.AsyncFlush`, `DB.Compact`, `DB.Ingest`, `DB.Get`, `DB.NewIter`, `Batch`, `Snapshot`, `Peek`, `GetVersion`, `checkConsistency`, `mkdirAllAndSyncParents`, file cache sharing, WAL replay, manifest replay, directory locking, cleaner behavior, shared-object file-number allocation, and read-only API enforcement.

## Risks and Edge Cases

- Many tests depend on carefully shaped LSM/WAL state. Changes to memtable growth, large-batch thresholds, flush scheduling, table-file naming, format marker names, or cleaner timing can invalidate assumptions.
- Randomized crash tests are high-value but can be seed-sensitive. Failures need seed preservation and may indicate real durability regressions.
- Some tests reach into internal mutex-protected state, so refactors of DB internals may require test rewrites even when public behavior is unchanged.
- Read-only behavior is subtle: replay must expose data without creating durable side effects or scheduling flushes.
- WAL failover and WAL recovery-dir compatibility guard against data loss; relaxing errors or path resolution can make missing WALs silently unrecoverable.
- The file-closure checker wraps selected tests and can surface leaks introduced by new open paths or early-return error handling.

## Test Signals

The whole file is test code. It provides direct signals for open-time correctness, crash safety, idempotent reopening, file naming, WAL corruption detection, read-only semantics, lock behavior, option compatibility, object-storage integration, and disabled-WAL behavior. Datadriven fixture coverage makes expected filesystem and LSM output explicit, while randomized crash tests broaden coverage over timing and durability interleavings.
