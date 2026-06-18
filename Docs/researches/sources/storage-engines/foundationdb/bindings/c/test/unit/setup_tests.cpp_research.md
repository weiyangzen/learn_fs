# sources/storage-engines/foundationdb/bindings/c/test/unit/setup_tests.cpp

## Purpose
`setup_tests.cpp` is a doctest unit test for C API setup and network initialization invariants.

## Important APIs, Types, and Functions
- `fdb_check` aborts on unexpected C API errors.
- The single `TEST_CASE("setup")` checks API version selection errors/success, max API version, network setup idempotence, network-thread completion hook registration, network run/stop, and hook invocation.

## Control Flow
Doctest provides `main`. The test first verifies selecting an excessive API version fails, selects the current API, verifies selecting again fails, sets up the network, verifies setup again fails, registers a completion hook, starts `fdb_run_network` on a thread, stops the network, joins, and checks the hook fired.

## State and Persistence Behavior
No database state is touched. The test mutates global FDB API process state, so it must run in a fresh process where API version and network are not already selected/setup.

## Dependencies and Integration Points
It uses the FDB C API, doctest, iostream, and C++ threads. It is part of C binding unit coverage for setup semantics.

## Risks
Because the API version and network state are global, this test cannot be safely composed with other tests in the same process. It assumes `FDB_API_VERSION` is valid and that network stop completes promptly.

## Test Signals
Passing the test validates correct errors for invalid/double setup calls and confirms completion hooks run after the network thread exits.
