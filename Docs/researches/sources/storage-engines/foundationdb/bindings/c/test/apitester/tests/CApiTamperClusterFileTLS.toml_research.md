# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiTamperClusterFileTLS.toml

## Purpose
Runs cluster-file tampering against a TLS-enabled cluster.

## Important APIs, types, and functions
Combines `tamperClusterFile`, `multiThreaded`, `buggify`, `[server] tls_enabled = true`, and one `ApiCorrectness` workload.

## Control flow
The runner passes TLS files while the executor mutates and restores a temporary cluster file.

## State and persistence behavior
Persists workload data after recovery and mutates temporary cluster-file state.

## Dependencies and integration points
Stresses TLS option application, cluster-file reload, database creation, and retry behavior together.

## Risks and test signals
TLS plus invalid cluster-file windows can expose longer delays or config mismatches. Success is clean recovery and workload completion.
