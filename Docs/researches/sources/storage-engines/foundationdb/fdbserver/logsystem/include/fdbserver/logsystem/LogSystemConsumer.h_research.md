# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystemConsumer.h

## Purpose
Declares a narrow consumer-facing wrapper around `LogSystem` so storage servers and other log readers can peek and pop without direct access to epoch recruitment, push, and recovery internals.

## Important APIs, Types, And Functions
`LogSystemConsumer` is reference-counted and stores a `Reference<LogSystem>`. It exposes `peekAll()`, `peekRemote()`, multiple `peek()` overloads, `peekLocal()`, `peekTxs()`, `peekSingle()`, `peekLogRouter()`, `popLogRouter()`, `popTxs()`, `pop()`, `getTxsPoppedVersion()`, `getEnd()`, and `getPseudoPopTag()`.

## Control Flow
Consumers call peek methods with a database ID, begin/end versions, tags, locality hints, and parallel-get-more options. The implementation constructs appropriate cursor combinations from current and old log generations. Consumers call pop methods after durable consumption to advance TLog pop state for data tags, TXS tags, or log-router tags.

## State And Persistence Behavior
The wrapper stores only the underlying `LogSystem` reference. Popping mutates `LogSystem` state and sends pop requests to TLogs in the implementation. Peek calls expose cursor state but do not themselves persist data.

## Dependencies And Integration Points
Depends directly on `LogSystem.h` and thus the cursor interfaces and log-system model. Used by storage servers, backup/range-backup consumers, transaction-state recovery through `LogSystemDiskQueueAdapter`, and resolver/proxy metadata mutation code.

## Risks And Edge Cases
Multiple peek modes differ subtly: local versus remote, TXS versus log-router, single-tag history versus multi-tag buffered reads, and use of satellite/known-stopped TLog IDs. Incorrect locality or end-version selection can over-read, under-read, or miss old generation data. Pop calls require durable-known-committed context for safe trimming.

## Test Signals
Signals are mostly integration-level: storage recovery, backup log reading, log-router tests, TXS transaction-state replay, and traces in `LogSystemConsumer.cpp` plus cursor traces in `LogSystemPeekCursor.cpp`.
