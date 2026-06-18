# sources/storage-engines/foundationdb/bindings/c/test/shim_lib_tester.cpp

## Purpose
`shim_lib_tester.cpp` is a command-line utility for validating FoundationDB C shim library configurations, including local client override, external client library, external client directory, disabled local client, and capped API version selection.

## Important APIs, Types, and Functions
- `TesterOptions` stores parsed CLI values.
- `TesterOptionDefs`, `parseArgs`, `processArg`, and `processIntOption` implement SimpleOpt parsing.
- `applyNetworkOptions` maps options to FDB network options or rejects invalid combinations.
- `testBasicApi` creates a database/transaction, sets a timeout, writes `key1=val1`, commits with retry handling, and exits on timeout.
- `testNewOnlyApi` is a placeholder for future shim compatibility probes.

## Control Flow
`main` parses options, optionally calls `fdb_shim_set_local_client_library_path` before any FDB API call, selects the requested capped API version, applies network options, sets up and runs the network on a thread, performs a basic write test, optionally flushes deferred cleanup under ASAN, stops the network, and joins.

## State and Persistence Behavior
The test writes one key/value pair to the configured cluster. It has no result file. Process exit code communicates success/failure to higher-level tests.

## Dependencies and Integration Points
It uses `test/fdb_api.hpp` C++ wrappers, `foundationdb/fdb_c_shim.h`, SimpleOpt, fmt, FDB error definitions, and network options for multi-version/external clients. It is likely invoked by Python shim tests.

## Risks
`fdb_check` accepts an expected-error parameter but ignores it. Invalid external-client configurations intentionally fail by timeout/exit, so calling tests must interpret exit codes carefully. The basic API test mutates a fixed key. ASAN-specific flushing depends on native C API calls.

## Test Signals
Exit code 0 after a commit validates the selected shim configuration. Negative tests should verify invalid library paths, disabled local client without external library, old API versions, and external-client directory behavior.
