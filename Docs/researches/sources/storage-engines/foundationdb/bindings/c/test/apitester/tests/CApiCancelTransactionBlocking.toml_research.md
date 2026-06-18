# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionBlocking.toml

## Purpose
Randomized multi-threaded cancel-transaction scenario using blocking future waits.

## Important APIs, types, and functions
Enables `multiThreaded`, `buggify`, and `blockOnFutures`, with randomized FDB threads, database pool size, client threads, and clients. Runs one `CancelTransaction` workload with random key/value sizes and operation counts.

## Control flow
The runner creates a temporary cluster, the tester randomizes configured ranges, and `BlockingTransactionContext` waits on futures from scheduler threads while cancel operations run.

## State and persistence behavior
The workload seeds and mutates a test key space in FDB. No TLS or server override is requested.

## Dependencies and integration points
Parsed by `TesterTestSpec.cpp`, launched by `run_c_api_tests.py`, and stresses blocking executor plus cancel workload behavior.

## Risks and test signals
Blocking waits can deadlock if scheduler capacity is insufficient. Clean tester exit and workload success logs are the signal.
