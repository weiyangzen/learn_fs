# sources/storage-engines/foundationdb/bindings/c/test/test.h

## Purpose
`test.h` is a header-only helper library for C binding tests and benchmarks. It supplies timing, deterministic key generation, median calculation, KPI/error result collection, JSON result writing, error handling, network thread startup, and database opening.

## Important APIs, Types, and Functions
- `getTime`, `writeKey`, `generateKeys`, `freeKeys`, `median`.
- `RunResult` and `RES` standardize benchmark function return values.
- `Kpi`, `Error`, and `ResultSet` form linked-list result storage.
- `newResultSet`, `addKpi`, `addError`, `writeResultSet`, and `freeResultSet` manage result lifecycle.
- `getError`, `checkError`, `logError`, and `maybeLogError` handle C API errors.
- `runNetwork` and `openDatabase` set up the FDB network thread and create a default database.

## Control Flow
Benchmarks include this header, create a `ResultSet`, select the API version, call `openDatabase`, add KPIs/errors while running, and call `writeResultSet`. Fatal errors write and free the result set before exiting.

## State and Persistence Behavior
`writeResultSet` persists a randomly named `fdb-c_result-<id>.json` file in the current directory. Other state is heap-owned linked lists and generated key arrays. `openDatabase` starts global FDB network state in a pthread.

## Dependencies and Integration Points
It depends on the FoundationDB C API and generated options, POSIX time, pthreads, sockets byte-order headers, and standard C allocation/IO. Multiple C test programs include it directly, so function definitions are emitted into each translation unit.

## Risks
There are no include guards, though each test likely includes it once. JSON output is hand-escaped and will break if KPI or error strings contain quotes or control characters. `freeKeys` frees only `0..numKeys-1` even though `generateKeys` allocates `numKeys + 1`, leaking the sentinel key. `runNetwork` signature omits a `void*` parameter expected by pthread start routines.

## Test Signals
Any benchmark using this header should produce a result JSON file with expected KPI names and an empty error array. Memory tooling would catch the sentinel key leak and result-list cleanup issues.
