# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ServerCheckpoint.h

## Purpose
`ServerCheckpoint.h` defines generic checkpoint reader/fetch/delete interfaces independent of a particular storage engine.

## Important APIs, Types, And Functions
`FDB_BOOLEAN_PARAM(CheckpointAsKeyValues)` controls checkpoint materialization mode. `ICheckpointIterator` batches key-value reads. `ICheckpointReader` supports `init`, `nextKeyValues`, `nextChunk`, `close`, optional `getIterator`, and `inUse`. Factory and utility functions include `newCheckpointReader`, `deleteCheckpoint`, `fetchCheckpoint`, `fetchCheckpointRanges`, `serverCheckpointDir`, and `fetchedCheckpointDir`.

## Control Flow
Fetch functions copy or convert checkpoint data to local directories, optionally checkpointing progress through a callback. Readers stream checkpoint contents as raw chunks or key-value batches, and implementations can expose range iterators.

## State And Persistence Behavior
The header operates over `CheckpointMetaData`, which records durable checkpoint identity, format, and locations. Directory helpers standardize server-side and fetched-checkpoint paths.

## Dependencies And Integration Points
It depends on Native API, storage checkpoint metadata, Flow futures, and storage-engine-specific implementations such as RocksDB checkpoint utilities. It integrates with data movement, recovery, backup/restore, and storage checkpoint transfer.

## Risks And Edge Cases
Incorrect format dispatch, lifecycle of raw `ICheckpointReader*`, progress callback failures, partial fetches, and chunk/key-value mode mismatches can corrupt movement or leak disk files.

## Test Signals
Tests should cover fetch resume, range fetch, directory naming, reader close behavior, chunk and key-value iteration, delete cleanup, and dispatch to each supported checkpoint format.
