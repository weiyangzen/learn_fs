# sources/storage-engines/foundationdb/bindings/c/test/client_memory_test.cpp

## Purpose
Stress utility for observing whether client memory is returned to the OS after large cancelled transaction allocations.

## Important APIs, types, and functions
Uses raw C API setup/run/stop plus `fdb_open_database`. Worker threads create `fdb::Transaction`, perform 10,000 `set` calls with growing zero-filled values, then cancel.

## Control flow
The program selects latest API, starts the network thread, enables JSON tracing, opens a database, runs 64 allocation-heavy threads, destroys the database, sleeps 10 seconds for external memory observation, and stops the network.

## State and persistence behavior
Transactions are cancelled, so no database mutations commit. Process memory and trace files are the observed state.

## Dependencies and integration points
Includes `foundationdb/fdb_c.h` and `unit/fdb_api.hpp`. Intended for memory/allocator tests with an external monitor.

## Risks and test signals
It prints usage but does not exit on wrong argc. The intended signal is RSS decreasing after handle destruction and sleep.
