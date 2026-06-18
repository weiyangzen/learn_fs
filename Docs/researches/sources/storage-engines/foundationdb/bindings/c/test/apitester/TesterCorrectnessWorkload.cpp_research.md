# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterCorrectnessWorkload.cpp

## Purpose
`TesterCorrectnessWorkload.cpp` defines `ApiCorrectnessWorkload`, the main randomized C API correctness workload for basic transaction operations: insert, get, getKey, clear, getRange, clearRange, and commit-then-read behavior.

## Important APIs, Types, And Functions
- `OpType` enumerates operation families.
- `randomCommitReadOp()` writes key/value pairs with read conflict ranges, updates the local store, then reads them back in a separate transaction, optionally using GRV cache for API >= 710.
- `randomGetOp()` issues concurrent gets and compares each result with `stores`.
- `randomGetKeyOp()` tests key selectors and adjusts results that fall outside the current workload key prefix.
- `getRangeLoop()` repeatedly calls `getRange()` using `more` and `firstGreaterThan(lastKey)` until exhausted.
- `randomGetRangeOp()` compares FDB range results with the local `KeyValueStore`.
- `randomOperation()` chooses a random operation, forcing insert when the local store is empty.
- Factory registration name is `"ApiCorrectness"`.

## Control Flow
Each operation uses asynchronous `execTransaction()` calls and scheduler continuations. Reads gather futures and continue after all complete; range reads loop across pages if `more` is true. Mutations update `stores` only after commit success through inherited helpers or explicit callbacks.

## State And Persistence Behavior
Persistent data is confined to the inherited workload key prefix. Local expected state is `stores[tenantId]`. `randomGetKeyOp()` acknowledges that real FDB contains data from other clients and maps results outside the workload prefix to start/end sentinels before comparing with the local model.

## Dependencies And Integration Points
It depends on `ApiWorkload`, `TesterUtil`, `fmt`, and `test/fdb_api.hpp`. It relies heavily on `TesterKeyValueStore` matching FoundationDB selector and range semantics for keys inside the workload prefix.

## Risks And Edge Cases
Range operations choose begin and end independently; if begin > end, the local comparison path may expose API assumptions depending on wrapper behavior. `getRangeLoop()` must clear results on retry to avoid duplicate accumulation. Key selector offsets are limited to 0..4 here, so negative selector coverage is elsewhere. GRV cache testing is API-version-gated.

## Test Signals
Logs and assertions report mismatches for get, getKey, getRange, and commit-read cases. This is a broad behavioral signal for C API transaction wrappers, future aggregation, retry handling, and local model consistency.
