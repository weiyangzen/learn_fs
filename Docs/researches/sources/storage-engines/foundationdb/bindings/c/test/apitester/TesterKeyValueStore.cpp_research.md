# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterKeyValueStore.cpp

## Purpose
`TesterKeyValueStore.cpp` implements the thread-safe in-memory ordered key/value model used by API tester workloads to compute expected FoundationDB results.

## Important APIs, Types, And Functions
- `get()` returns an optional value for a key.
- `exists()` checks key presence.
- `getKey()` models FoundationDB key-selector semantics over the ordered map.
- `getRange()` returns ordered or reverse key/value slices with a limit.
- `set()`, `clear(key)`, and `clear(begin,end)` mutate the model.
- `size()`, `startKey()`, `endKey()`, and `printContents()` provide support/debug APIs.

## Control Flow
All methods take a mutex. Selector logic starts at `lower_bound(keyName)`, adjusts for `orEqual` and offset direction, walks the map, and returns either a real key or start/end sentinel. Range logic scans from `lower_bound(begin)` forward until `end` or limit, or backward from `lower_bound(end)` for reverse mode.

## State And Persistence Behavior
State is local process memory: `std::map<fdb::Key, fdb::Value, std::less<>> store` plus a mutex. It mirrors expected persistent database contents for a workload prefix but is not itself persisted.

## Dependencies And Integration Points
It includes `TesterKeyValueStore.h` and uses FoundationDB C++ wrapper types from `TesterUtil.h`. `ApiWorkload` owns one store per optional tenant id.

## Risks And Edge Cases
`getKey()` must match FDB key selector semantics; subtle off-by-one differences can create false test failures or miss real API bugs. Reverse `getRange()` is implemented but noted as not currently tested because reverse range queries are disallowed at the API level in that context. `printContents()` assumes keys are printable C strings, which may not hold for arbitrary binary keys.

## Test Signals
It is an oracle rather than a test target. Correctness workloads compare live C API results against this model, so its behavior directly determines test quality.
