# sources/storage-engines/tikv/components/raftstore-v2/src/operation/mod.rs

## Purpose
Defines the operation module boundary for raftstore-v2 and re-exports the command, lifecycle, ready, query, transaction extension, disk snapshot backup, and unsafe recovery pieces used by the rest of the crate.

## Important APIs, Types, And Functions
Top-level submodules include `bucket`, `command`, `disk_snapshot_backup`, `life`, `misc`, `pd`, `query`, `ready`, `txn_ext`, and `unsafe_recovery`. Public re-exports expose command structures such as `CommittedEntries`, `CompactLogContext`, split and merge helpers, `DestroyProgress`, `AbnormalPeerContext`, `GcPeerContext`, and ready types such as `ApplyTrace`, `AsyncWriter`, `ReplayWatch`, `SnapState`, and `StateStorage`. Crate-visible exports expose `SplitInit`, `LocalReader`, `ReadDelegatePair`, `SharedReadTablet`, and `TxnContext`.

## Control Flow
The file has no runtime control flow outside test utilities. It establishes import paths and module ownership so peer/store FSM code can refer to operation helpers through a stable facade.

## State And Persistence Behavior
The module root does not persist state. Its re-exports expose persistence-sensitive helpers, especially command apply state, lifecycle tombstone state, and ready apply-trace state.

## Dependencies And Integration Points
It is the integration point for raftstore-v2 operation code. Test utilities provide `create_tmp_importer`, `MockReporter`, `new_put_entry`, and `new_delete_range_entry`, which support apply/query tests by building encoded raft log entries and receiving apply results.

## Risks And Edge Cases
The main risk is API surface drift: moving or renaming re-exports can break consumers outside this directory. The test utilities encode requests using `SimpleWriteEncoder` and region headers, so they must stay aligned with command decoding.

## Test Signals
No tests are defined directly here, but `test_util` is used by operation submodule tests such as capture/apply-trace tests. Compilation is the primary signal for export correctness.
