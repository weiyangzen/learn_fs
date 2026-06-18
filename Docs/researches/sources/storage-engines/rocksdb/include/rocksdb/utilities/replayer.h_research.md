# sources/storage-engines/rocksdb/include/rocksdb/utilities/replayer.h

## Purpose
Defines the query trace replay interface for replaying captured RocksDB operations with optional timing and concurrency controls.

## Important APIs, Types, And Functions
`ReplayOptions` configures `num_threads` and `fast_forward`. `Replayer` exposes `Prepare`, `GetHeaderTimestamp`, `Next`, `Execute`, and `Replay`.

## Control Flow, State, And Persistence
Callers prepare/reset the replayer, read records with `Next`, execute individual records with `Execute`, or replay the full stream with `Replay`. Executed operations may mutate the target DB; trace input is read-only.

## Dependencies And Integration Points
Depends on trace record/result types, callbacks, and `Status`. Integrates with `DB::NewDefaultReplayer`, trace readers, and benchmark replay workflows.

## Risks And Edge Cases
`Incomplete` signals unprepared or exhausted state. Unsupported trace records return `NotSupported`. Multi-thread replay and speed scaling can change timing-sensitive behavior. Operation-specific not-found results can still be wrapped in `Status::OK()` execution status.

## Test Signals
Cover prepare/reset, header timestamp, end-of-stream, unsupported records, callback delivery, operation result capture, timing scaling, and multi-thread replay.
