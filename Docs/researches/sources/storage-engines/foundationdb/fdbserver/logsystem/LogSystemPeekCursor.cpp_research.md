# sources/storage-engines/foundationdb/fdbserver/logsystem/LogSystemPeekCursor.cpp

## Purpose
Implements the concrete log peek cursor stack used by FoundationDB recovery and log consumers to read ordered log messages from one TLog, from replicated TLogs, across multiple log sets, across epoch history, or through a buffering merge. It is the runtime implementation behind the cursor declarations in `LogSystemTypes.h` and the `IPeekCursor`/`IReplayPeekCursor` contracts in `LogSystem.h`.

## Important APIs, Types, And Functions
`ServerPeekCursor` reads one TLog via `TLogInterface::peekMessages` or `peekStreamMessages`. `MergedPeekCursor` merges replicas within one log set by quorum or replication policy. `SetPeekCursor` merges candidate `LogSet`s and prefers a best set/server when available. `ReplayMultiCursor` and `MultiCursor` stitch epoch ranges. `BufferedCursor` preloads and sorts messages from multiple cursors. Helper actors include `tryEstablishPeekStream`, `serverPeekParallelGetMoreImpl`, `serverPeekStreamGetMoreImpl`, `serverPeekGetMoreImpl`, `mergedPeekGetMore`, `setPeekGetMore`, `bufferedGetMoreLoader`, and `bufferedGetMore`.

## Control Flow
`ServerPeekCursor::getMore()` returns immediately when a message is already buffered for non-parallel peeks; otherwise it chooses streaming, parallel, or single-request peek paths. Replies are normalized through `updateCursorWithReply()`, which resets the arena reader, updates spilled/popped state, advances to the prior cursor position, and exposes the next message. Merge cursors repeatedly request data from a preferred active cursor or enough peer cursors to make progress, then select a message version by best-server, read quorum, or policy satisfaction. Multi cursors drop completed epoch-range cursors once the active cursor reaches its epoch end. Buffered cursor loaders fill per-source queues until a common minimum version boundary allows globally ordered output.

## State And Persistence Behavior
The file does not write durable state; it tracks transient read state in arenas, readers, message versions, popped versions, outstanding futures, reply streams, locality/policy metadata, and buffered queues. `popped()` aggregates observed popped versions so consumers can discard safe ranges. `getMinKnownCommittedVersion()` and `getMaxKnownVersion()` expose TLog progress returned in peek replies. Connection reset metrics are maintained per cursor and may reset a transport connection after slow peek statistics cross knob thresholds.

## Dependencies And Integration Points
The implementation depends on `TLogInterface` RPC endpoints, `FailureMonitor`, Flow futures/coroutines, `SERVER_KNOBS`, replication policy helpers, `LocalitySet`, `TagsAndMessage`, and debug trace utilities. It is used by `LogSystemConsumer.cpp` to construct peek cursors for storage, log-router, TXS, and recovery paths. Version-vector unicast recovery integrates through `knownLockedTLogIds`, `bestServer`, and `returnEmptyIfStopped` behavior.

## Risks And Edge Cases
Peek progress depends on correctly handling interface changes, end-of-stream, broken promises, and request timeouts. Parallel peeks must reject stale replies whose begin version does not match the expected begin. Streaming peeks must reset on connection failure, obsolete operations, or maybe-delivered requests. Merge selection can advance past a target sequence when one replica lacks the exact message, so the code loops until stable and emits probes. Version-vector unicast empty-range returns are intentionally conservative when best-set information is unclear. Buffered cursor `isExhausted()` is asserted false and should not be used as a reliable exhaustion signal.

## Test Signals
Signals include Flow unit/simulation tests that exercise log recovery, storage-server log replay, transaction-state recovery, and version-vector unicast paths. Runtime trace events such as `SPC_GetMore`, `PeekReplyTimeout`, `SlowPeekStats`, and merge/set cursor probes help diagnose stalls, slow TLogs, stale endpoints, and policy-selection issues.
