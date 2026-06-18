<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/reduce_test.go -->
# sources/storage-engines/pebble/internal/metamorphic/reduce_test.go

Purpose: implements a reducer for metamorphic failures, attempting to remove operations and simplify keys while preserving a reproduction.

Important APIs/types: `tryToReduce`, `tryToReduceCompare`, `reducer`, `testConfig`, `makeReducer`, `setupRunDirs`, `getKeyFormat`, `try`, `Run`, `randomSubset`, and `shellJoin`.

Control flow and state: the reducer reads an existing `ops` file and selected run `OPTIONS`, creates fresh reduce directories under the configured test state root, and re-runs the current test binary with either `--run-dir` or `--compare`. If the reduced run still fails for the target reason, it saves logs and optional diagrams, deletes the previously saved reduced directory, and continues. `Run` decreases random removal probability over time, then tries key simplification with and without suffix retention.

Persistence and integration: writes new `reduce-*` directories, `ops`, `OPTIONS`, `log`, and optional `diagram`. It integrates with the current test binary via `os.Args[0]`, `metamorphic.TryToGenerateDiagram`, and `TryToSimplifyKeys`. Risks include nondeterministic failures, hard-coded internal-error filters, fixed 10s timeout during reduction, potentially many subprocesses, and deletion of previous saved reductions. Test signal is operational rather than unit-tested here.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/reduce_test.go -->
