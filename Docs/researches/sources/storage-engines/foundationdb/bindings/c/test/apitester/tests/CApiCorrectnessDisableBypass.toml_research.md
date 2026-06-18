# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessDisableBypass.toml

## Purpose
Runs single-threaded API correctness with client bypass disabled.

## Important APIs, types, and functions
Sets `multiThreaded = false`, `disableClientBypass = true`, small client/database ranges, and the three correctness workloads.

## Control flow
The tester applies `FDB_NET_OPTION_DISABLE_CLIENT_BYPASS` when supported before running workloads.

## State and persistence behavior
Persists normal correctness workload data; the important state is process-global client network configuration.

## Dependencies and integration points
Exercises disable-bypass option application and baseline workload execution without buggify.

## Risks and test signals
API-version gating or bypass path changes can affect behavior. Passing indicates correctness through the non-bypass client path.
