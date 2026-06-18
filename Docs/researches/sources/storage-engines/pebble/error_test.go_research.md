# sources/storage-engines/pebble/error_test.go

## Purpose
Exercises Pebble's error propagation and crash recovery behavior under injected filesystem failures, read corruption, WAL rotation crashes, and compaction-time crash scenarios.

## Important APIs, Types, And Functions
`panicLogger` converts fatal logging into panics so tests can observe fatal paths. `corruptFS` and `corruptFile` mutate bytes returned by `Read`/`ReadAt`. `expectLSM` checks manifest layout. Tests include `TestErrors`, `TestRequireReadError`, `TestCorruptReadError`, `TestDBWALRotationCrash`, and `TestDBCompactionCrash`.

## Control Flow
`TestErrors` repeatedly runs open, set, flush, compact, iterate, and close with an injected error at successive operation indices until a clean run occurs, then checks expected fatal manifest errors appeared. Read tests build a controlled LSM with range deletion and point data, enable read error or corruption injection, iterate, and require any injected read failure to surface through iterator close or operation errors. Crash tests use crashable MemFS clones to simulate unsynced writes being lost and then reopen/continue.

## State And Persistence Behavior
The tests stress durable metadata, WALs, flushed SSTables, compaction output, and recovery from partially persisted filesystem state. They intentionally clone crash states and reopen DBs to verify persisted state is recoverable or that errors are reported rather than silently ignored.

## Dependencies And Integration Points
Uses `vfs`, `errorfs`, `leaktest`, test key generators, format versions, compaction options, and Pebble public APIs. The cases exercise Open/Close, WAL management, flush, compaction, iterator reads, checksums, and manifest update paths.

## Risks And Edge Cases
Important coverage includes retried background write errors, mandatory foreground read-error reporting, checksum/corruption detection when the FS returns successful reads with bad bytes, crash points during WAL rotation, concurrent compactions with random latency, and Windows-specific timing avoidance.

## Test Signals
Signals are absence of unexpected non-injected errors, expected injected-error messages, iterator close errors when reads fail, corruption errors for modified bytes, and successful reopen after simulated crashes.
