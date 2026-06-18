# sources/storage-engines/foundationdb/fdbserver/logrouter/LogRouter.cpp

## Purpose
This file implements the log router actor. A log router pulls mutation data from satellite or primary TLogs, buffers it by remote-log tag, serves peek and streaming peek requests from remote TLogs, accepts pop requests, and exits when removed from the cluster configuration.

## Important APIs, Types, And Functions
`LogRouterData` owns all runtime state. Nested `TagData` stores per-tag `version_messages`, pop version, durable known committed version, and `eraseMessagesBefore`. Other important methods are `commitMessages`, `waitForVersion`, `waitForVersionAndLog`, `getPeekCursorData`, `pullAsyncData`, `peekMessagesFromMemory`, templated `logRouterPeekMessages`, `logRouterPeekStream`, and `cleanupPeekTrackers`. Free actors are `logRouterPop`, `logRouterCore`, `checkRemoved`, and exported `logRouter`.

## Control Flow
`logRouter` traces startup, runs `logRouterCore`, and races it with `checkRemoved`. `logRouterCore` starts data pulling, peek-tracker cleanup, and role tracing, then services database info changes, peek requests, streaming peek requests, and pop requests through an actor collection. `pullAsyncData` obtains an `IReplayPeekCursor`, switches between satellite and primary locations on slow peeks, groups messages by version, maps primary tags to remote-log tags via `LogSet::getPushLocations`, waits for safe buffering windows, commits messages to memory, and advances `version`. Peek requests wait for availability unless `returnIfBlocked`, serialize version headers and messages from memory, handle sequence tracking for parallel get-more requests, and return `TLogPeekReply`.

## State And Persistence Behavior
The router is memory-buffered. `messageBlocks` owns arenas for message bytes, and each tag stores `LengthPrefixedStringRef` references into those blocks. Pop requests advance per-tag popped versions, erase old per-tag messages, drop old message blocks, update `minPopped`, compute popped durable version, and optionally pop the upstream log system once recovery is fully recovered. No local disk persistence is performed.

## Dependencies And Integration Points
It integrates with `TLogInterface` request streams, `LogSystemConsumer`, `LogSystemFactory`, `IReplayPeekCursor`, `ServerDBInfo`, recovery state, Flow actors, counters, histograms, event cache tracking, and knobs controlling buffering, peek batching, slow-peek switching, tracker expiration, and replacement grace periods.

## Risks And Test Signals
Backpressure is delicate: `waitForVersion` must prevent unbounded buffering while still handling epoch end and replacement routers. Message refs rely on `messageBlocks` lifetime. Sequence tracking must avoid stuck or divergent parallel peeks. Removal logic must not kill replacement routers before configuration catches up. Tests should cover startup handoff, replacement start at cursor popped version, peek empty batching, stream peeks, return-if-blocked, sequence retries/obsolete paths, pop cleanup, slow-peek failover, recovery-state-controlled upstream pops, and worker removal.
