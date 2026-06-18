# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessTLS.toml

## Purpose
Runs multi-threaded buggified correctness workloads against a TLS-enabled cluster.

## Important APIs, types, and functions
Combines randomized multi-threaded settings with `[server] tls_enabled = true` and workloads `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
The runner provisions TLS material and the tester applies TLS network options before executing workloads.

## State and persistence behavior
Persists workload data over TLS connections; certificates are temporary runner state.

## Dependencies and integration points
Covers TempCluster TLS setup, tester TLS options, FDB connectivity, and core workloads.

## Risks and test signals
Certificate path, TLS/plaintext mismatch, and option ordering are key risks. Clean workload completion is the signal.
