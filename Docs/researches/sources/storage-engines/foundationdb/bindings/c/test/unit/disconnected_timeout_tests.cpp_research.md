# sources/storage-engines/foundationdb/bindings/c/test/unit/disconnected_timeout_tests.cpp

## Purpose
`disconnected_timeout_tests.cpp` is a doctest suite for C API transaction and database timeout behavior when connected to an unavailable cluster file.

## Important APIs, Types, and Functions
- `fdb_check`, `fdb_open_database`, and `wait_future` wrap C API error handling.
- `validateTimeoutDuration` asserts actual timeout duration is at least expected and less than double expected.
- Test cases cover transaction timeout before/after operations, timeout replacement, database timeout, database vs transaction precedence, reset behavior, reset/destruction cancellation, and repeated timeout setup/destruction.
- `main` handles unavailable cluster file, optional external client library, doctest context, network setup/run/stop, and global DB handles.

## Control Flow
The program selects the latest API, optionally configures an external client, starts the FDB network, opens two database handles against an unavailable cluster, runs doctest cases, destroys handles, stops network, and returns doctest status.

## State and Persistence Behavior
No database persistence is expected because the cluster is unavailable. State consists of global `FDBDatabase*` handles and futures that should timeout or be canceled. The tests intentionally block until timeout/cancel readiness.

## Dependencies and Integration Points
It uses the FDB C API directly and the local unit `fdb_api.hpp` RAII wrappers for futures/transactions. It depends on doctest and C++ threading/chrono.

## Risks
Wall-clock assertions can be flaky on very slow or overloaded machines. Error-code checks use numeric constants `1031` and `1025` rather than named constants. Tests require a genuinely unavailable cluster file; an accidentally reachable cluster changes behavior. Database timeout is set on a shared `timeoutDb`, so tests depend on set/reset semantics across transaction creation.

## Test Signals
Passing doctest output validates timeout duration, precedence, reset cancellation, destruction cancellation, and external-client timeout support. Failures are strong signals for C API timeout regressions.
