# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterOptions.h

## Purpose
`TesterOptions.h` defines the aggregate command-line/configuration state for the C API tester executable.

## Important APIs, Types, And Functions
- `TesterOptions` fields include API version, cluster file, tracing options, external/future client library paths, temp directory, local-client disable flag, test file path, pipe names, transaction retry limit, thread/database/client counts, stats interval, parsed `TestSpec`, blob granule base path, TLS files, and retain-client-library-copy flag.

## Control Flow
There is no method logic here. Argument parsing and test runner code populate the struct, then downstream setup uses it to configure network options, workloads, clients, and tests.

## State And Persistence Behavior
The struct is process-local configuration. Fields such as trace directory, temp directory, external client library, and TLS paths affect filesystem/network behavior elsewhere.

## Dependencies And Integration Points
It includes `TesterTestSpec.h`, whose `FDB_API_VERSION` default is used for `apiVersion`. It is consumed by `fdb_c_api_tester.cpp` and related runner code.

## Risks And Edge Cases
Uninitialized integer fields (`numFdbThreads`, `numClientThreads`, `numDatabases`, `numClients`) rely on parser/defaulting elsewhere before use. Path fields must be validated by consumers. Retaining client library copies can intentionally leave files for debugging.

## Test Signals
Compile coverage validates the option aggregate. Runtime command-line tests and API tester invocations validate that fields are populated and honored.
