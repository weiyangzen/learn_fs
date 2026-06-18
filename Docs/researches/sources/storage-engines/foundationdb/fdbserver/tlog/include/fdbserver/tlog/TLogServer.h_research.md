# sources/storage-engines/foundationdb/fdbserver/tlog/include/fdbserver/tlog/TLogServer.h

## Purpose
This header is the public declaration for the transaction log server actor used by worker startup and tests. It intentionally exposes a small surface: disk-space threshold helper, the `tLog` actor factory, and a `TLogFn` function-pointer alias.

## Important APIs, Types, And Functions
`effectiveTLogMinAvailableSpaceRatio()` returns the runtime minimum available-space ratio for TLog recovery writes, with simulation-specific behavior implemented in the `.cpp`. `tLog(...)` accepts persistent KV and queue storage, database info, locality, initialization request stream, TLog/worker IDs, restore flag, old/recovered promises, data folder, degraded and low-disk state variables, active shared TLog tracking, and the health-check toggle. `using TLogFn = decltype(&tLog);` enables dependency injection or typed references to the actor.

## Control Flow
Callers create or pass persistent stores, then call `tLog`. The actor initializes storage, optionally restores from disk, handles future recruitment requests from `tlogRequests`, and completes or errors the supplied promises.

## State And Persistence Behavior
The header does not define state. Its signature makes persistence explicit through `IKeyValueStore*`, `IDiskQueue*`, `restoreFromDisk`, folder naming, and shared state references for recovery/degradation.

## Dependencies And Integration Points
It includes `TLogInterface` and Flow primitives and forward-declares storage and server-info types. Worker code, tests, and TLog recruitment paths consume this API.

## Risks And Test Signals
The broad parameter list is a stability contract: changes ripple into worker startup and tests. The raw storage pointers imply ownership and close/dispose behavior must remain clear in the implementation.
