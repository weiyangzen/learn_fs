# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionDBPerTX_TLS.toml

## Purpose
Runs database-per-transaction cancellation against a TLS-enabled temporary cluster.

## Important APIs, types, and functions
Combines `databasePerTransaction`, `multiThreaded`, `buggify`, `[server] tls_enabled = true`, and one `CancelTransaction` workload.

## Control flow
`run_c_api_tests.py` provisions TLS material and passes TLS paths; the tester repeatedly creates database handles and cancels transactions over TLS.

## State and persistence behavior
Persists workload keys in the TLS cluster and uses runner-managed certificate files.

## Dependencies and integration points
Integrates TempCluster TLS setup, tester TLS network options, database-per-transaction execution, and cancellation.

## Risks and test signals
TLS connection setup plus database churn can expose timeout, certificate, or cleanup issues. Success is normal workload completion.
