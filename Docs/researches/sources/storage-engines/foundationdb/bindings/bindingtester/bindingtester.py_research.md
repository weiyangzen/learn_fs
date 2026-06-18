# sources/storage-engines/foundationdb/bindings/bindingtester/bindingtester.py

## Purpose
This executable Python driver generates FoundationDB binding tests, inserts instruction streams into a cluster, runs one or two language-specific testers, compares outputs, validates test-specific invariants, supports printing and bisection, and manages CLI options.

## Important APIs, Types, And Functions
`API_VERSIONS` lists supported API versions and is asserted to end at `FDB_API_VERSION`. `ResultSet` aligns and compares tester outputs. `choose_api_version` validates or randomly selects a compatible API version. `TestRunner` owns DB connection, tester selection, test generation, insertion, process execution, result collection, and validation. Top-level helpers are `bisect`, `parse_args`, `validate_args`, and `main`.

## Control Flow
`main` parses args, configures logging, sets a random seed and optional tracing, constructs `TestRunner`, then dispatches to bisect, print, insert-only, or run. `TestRunner.run_test` generates instructions, inserts them before each tester, calls `pre_run`, executes external tester commands with timeout, reads output subspaces, and compares results. `ResultSet.check_for_errors` walks ordered result lists, aligns by sequence number or minimum tuple key, filters permissible global errors, and counts mismatches.

## State And Persistence Behavior
The driver deletes all keys in the connected database before inserting each test instruction set. Testers write result key-values into output subspaces. The driver itself maintains in-memory selected API/tester/test options, random seeds, and subprocess state.

## Dependencies And Integration Points
It integrates with the FoundationDB Python binding, tuple/subspace APIs, bindingtester test classes, known tester registry, utility logging, and external tester binaries/scripts for Python, Ruby, Java, Go, Flow, and Swift.

## Risks And Edge Cases
`del self.db[:]` is destructive to the selected cluster and assumes a disposable binding-test database. Command splitting uses `test.cmd.split(" ")`, so quoted paths/arguments are fragile. Timeout kills only the direct process. Concurrent tests cannot be compared. Random API-version selection calls `random.random` multiple times, so branch probabilities are sequential rather than a single distribution.

## Test Signals
Exit codes distinguish tester execution failure, comparison/validation failure, and driver exceptions. Logs include seed, operation count, API version, tester commands, incorrect result blocks, and filtered nondeterministic errors.
