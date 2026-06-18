# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemTypes.h

## Purpose
Declares concrete log-system data structures and cursor classes that are implemented across `LogSystem.cpp`, `LogSet.cpp`, and `LogSystemPeekCursor.cpp`.

## Important APIs, Types, And Functions
`LogSet` models one replicated log-set with TLogs, routers, backup workers, connection/push metrics, replication factor, write anti-quorum, locality data, policy, satellite tag locations, and push-location helpers. Cursor classes include `ServerPeekCursor`, `MergedPeekCursor`, `SetPeekCursor`, `ReplayMultiCursor`, `MultiCursor`, and `BufferedCursor`. `BufferedCursor::BufferedMessage` stores arena-owned message, tags, and version for sorted merge output.

## Control Flow
`LogSet` constructors convert `TLogSet`/`CoreTLogSet` config into runtime interfaces and locality/policy data. `getPushLocations()` maps tags to TLog indexes for writing. Cursor classes expose a common flow: `getMore()`, inspect `hasMessage()`, read message/tags, `nextMessage()`, advance or clone if needed. Merge/set cursors combine multiple `ServerPeekCursor`s, multi cursors sequence epochs, and buffered cursors reorder batched input from multiple sources.

## State And Persistence Behavior
These classes hold in-memory routing, cursor, arena, message, future, locality, replication-policy, and pop-version state. They do not persist directly; persistent log data lives in TLogs and core-state/log-system config. `LogSet` stores backup-worker and log-router interfaces that affect external state through other implementation files.

## Dependencies And Integration Points
Depends on `LogSystemConfig` and `DBCoreState`; cursor inheritance depends on interfaces from `LogSystem.h`. The types integrate with log pushing, log-system recovery, consumer peek methods, replication policy checks, backup worker assignment, and old-generation replay.

## Risks And Edge Cases
`LogSet` routing must preserve tag locality mapping, satellite tag tables, replication policy membership, and write anti-quorum assumptions. Cursor clones must be no-more snapshots that do not accidentally continue network reads. Buffering and merge cursors depend on stable `LogMessageVersion` ordering and arena lifetimes. Locality and known locked/stopped TLog IDs affect version-vector unicast safety.

## Test Signals
Signals include log-system cursor behavior, old-generation replay, backup/log-router recovery, push-location tests, and traces from `LogSystemPeekCursor.cpp` and `LogSet.cpp`.
