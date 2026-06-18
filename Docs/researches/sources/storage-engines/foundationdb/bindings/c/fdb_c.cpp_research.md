# sources/storage-engines/foundationdb/bindings/c/fdb_c.cpp

## Purpose
`fdb_c.cpp` implements FoundationDB's exported C API over the internal C++ `IClientApi`, `IDatabase`, `ITransaction`, and thread-safe future/result abstractions. It also handles API-version selection and compatibility dispatch for changed/removed functions.

## Important APIs, Types, And Functions
- Global `g_api_version` records the selected runtime API version.
- Cast macros map opaque C handles to internal types: `FDBFuture`/`FDBResult` to `ThreadSingleAssignmentVarBase`, `FDBDatabase` to `IDatabase`, `FDBTransaction` to `ITransaction`, and legacy `FDBCluster` to a stored cluster path.
- Error macros `RETURN_FUTURE_ON_ERROR`, `RETURN_RESULT_ON_ERROR`, `RETURN_ON_ERROR`, `CATCH_AND_RETURN`, and `CATCH_AND_DIE` convert C++ exceptions to C API error codes or error futures/results.
- Network/database functions include `fdb_network_set_option`, `fdb_setup_network_impl`, `fdb_run_network`, `fdb_stop_network`, `fdb_create_database`, and `fdb_create_database_from_connection_string`.
- Future/result functions expose cancellation, destruction, blocking, callbacks, error/value/key/range/string/key-array accessors, and synchronous `FDBResult` range access.
- Transaction functions implement read version, get/getKey/getRange/mapped range, set/clear/atomic/watch/commit, versionstamp, options, retry `on_error`, reset, conflict ranges, estimated size, and split points.
- `validate_and_update_parameters()` normalizes range limits, target bytes, streaming mode, iteration, and legacy reverse limit behavior.
- `fdb_select_api_version_impl()` enforces single selection, validates runtime/header versions, initializes platform/error state, and binds generated function pointers for compatibility variants.

## Control Flow
Most exported functions cast opaque handles, invoke the matching internal API method, and return either `fdb_error_t` or an extracted future pointer. API-version selection must happen once; after internal `selectApiVersion`, it applies `FDB_API_CHANGED` and `FDB_API_REMOVED` macros from newest to oldest so generated assembly trampolines dispatch each public symbol to the correct implementation for the selected header/runtime version.

## State And Persistence Behavior
Persistent database state is modified only through transaction/database operations. Process-local state includes `g_api_version`, generated function pointer globals, and the multi-version API singleton. Futures own result memory until the caller destroys/releases them. Database and transaction handles are reference-counted internal objects exposed as opaque pointers.

## Dependencies And Integration Points
This file depends on `fdbclient/FDBTypes.h`, `flow/ProtocolVersion.h`, multi-version transaction/client headers, `foundationdb/fdb_c.h`, `fdb_c_internal.h`, and generated `fdb_c_function_pointers.g.h`. It is compiled into `libfdb_c` and is the ABI consumed by all C bindings and many higher-level language bindings.

## Risks And Edge Cases
Memory lifetime is central: returned `uint8_t const*` arrays point into future/result-owned storage. Calling public API functions from removed-function implementations can accidentally resolve to a primary library under multi-version loading, which the file explicitly warns against. Range parameter compatibility for API <= 13, exact streaming with unlimited limits, iterator mode iteration bounds, tenant functions removed in 8.0 but still loaded by old Python bindings, and API selection after first call are all compatibility-sensitive. Several functions abort on unexpected deleted experimental tenant calls.

## Test Signals
Signals come from C unit tests, external-client tests, shim tests, C90 header tests, API tester workloads, binding tests, and upgrade tests configured by `CMakeLists.txt`. Static assertions check C/C++ layout compatibility for key-value and blob granule mutation enum values.
