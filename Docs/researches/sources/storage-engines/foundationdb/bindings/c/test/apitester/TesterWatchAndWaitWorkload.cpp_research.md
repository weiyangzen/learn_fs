# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWatchAndWaitWorkload.cpp

## Purpose
Defines the `WatchAndWait` workload, verifying that a watch future fires after a key changes.

## Important APIs, types, and functions
`WatchAndWaitWorkload` derives from `ApiWorkload`, overrides `getMaxSelfBlockingFutures`, and implements `randomOperation` with `set`, `get`, `watch`, `commit`, and `continueAfterAll`.

## Control flow
The workload writes an initial value, reads the key, creates a watch if needed, commits the watch transaction, and schedules a sibling transaction to write a distinct new value.

## State and persistence behavior
It persists random keys and values in the test cluster. It loops until the new value differs from the initial value so the watch has a real change to observe.

## Dependencies and integration points
Depends on `TesterApiWorkload.h`, `test/fdb_api.hpp`, and workload factory registration. Included by correctness TOML suites.

## Risks and test signals
Blocking mode must reserve enough threads for its one self-blocking future. Failures expose watch delivery, commit ordering, cancellation, and callback scheduling bugs.
