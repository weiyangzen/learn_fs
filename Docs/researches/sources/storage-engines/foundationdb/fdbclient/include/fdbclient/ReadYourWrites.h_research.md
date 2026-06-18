# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/ReadYourWrites.h

## Purpose
`ReadYourWrites.h` declares the RYW transaction wrapper that presents FoundationDB's normal transaction API while merging local writes with snapshot reads. It owns the snapshot cache, write map, conflict tracking, special key space writes, debug retry logging, timeout/retry state, and the underlying native `Transaction`.

## Important APIs, Types, And Functions
- `ReadYourWritesTransactionOptions` tracks RYW disablement, read-ahead, system key access, conflict disabling for the next write, retry logging, used-during-commit protection, special key space relaxation/configuration, timeouts, max retries, snapshot RYW, and unreadable bypass.
- `TransactionDebugInfo` stores transaction name and last retry log timestamp.
- `ReadYourWritesTransaction` exposes read APIs, mapped range reads, storage size/split helpers, conflict range APIs, writes/clears/atomic ops, watches, commit, versionstamp, options, retry handling, reset/cancel, debug traces/messages, and conflict range special-key readers.
- Private state includes `Arena`, native `Transaction`, `SnapshotCache`, `WriteMap`, read conflict map, watch map, reset promise, pending read aggregate, retries, approximate size, timeout actor, versionstamp state, native conflict range snapshots, special key write map, persistent option vectors, and sensitive option vectors.

## Control Flow And State
When RYW is enabled, reads use the native transaction with snapshot semantics and merge results through `SnapshotCache`, `WriteMap`, and `RYWIterator`. Writes update the write map and conflict maps before being pushed to the native transaction at commit. `pendingReads()` gates resets and commit-time used-during-commit protection. `onError()` resets state and reapplies persistent options. `getAndResetWriteConflictDisabled()` gives one-shot control for conflict range suppression.

## Persistence And External State
The wrapper itself is in-memory, but it accumulates mutations and conflict ranges that are eventually written by the native `Transaction`. Special key space writes are staged in `specialKeySpaceWriteMap` and committed via special key implementations. Persistent and sensitive transaction options survive retries. Debug messages/traces and JSON validation of special key errors are simulation-observable.

## Dependencies And Integration Points
It depends on `NativeAPI.actor.h`, status JSON parsing, key range maps, `RYWIterator`, `FastRef`, `WipedString`, `SnapshotCache`, and `WriteMap`. It is the transaction type used by bindings and internal helpers that need read-your-writes semantics. It also integrates with special key space, watches, versionstamps, conflict range introspection, tag throttling cost metrics, and status JSON fetch.

## Risks And Edge Cases
Returned values can hold the transaction arena alive, so long-lived values retain transaction memory. RYW-disabled mode delegates more behavior to `Transaction` and uses native conflict range snapshots after commit. Versionstamp operations can mark sections unreadable unless bypassed. Commit-time use protection, pending reads, and reset promises are concurrency-sensitive. Special key errors are expected to be valid JSON in simulation.

## Test Signals
Tests should cover read-after-set/clear/atomic behavior, range merge ordering, snapshot reads, conflict maps, watches, commit retry, persistent option replay, sensitive option handling, timeout/max retry behavior, special key writes and errors, versionstamp unreadable ranges, memory arena retention, debug trace logging, and RYW-disabled parity with native transaction behavior.
