# sources/storage-engines/pebble/metamorphic/meta.go

## Purpose
`meta.go` orchestrates full metamorphic test runs: building options, generating operations, launching child test executions, replaying one run, comparing histories, and providing run-level options. It is the package's top-level harness for "same logical operations under different Pebble configurations should produce equivalent histories."

## Important APIs, Types, and Functions
- `RunOption` and implementations configure `RunAndCompare`: `Seed`, `ExtendPreviousRun`, `UseDisk`, `UseInMemory`, `OpCount`, `RuntimeTrace`, `InnerBinary`, `ParseCustomTestOption`, `AddCustomRun`, `KeepData`, `InjectErrorsRate`, `MaxThreads`, `OpTimeout`, `FailOnMatch`, `MultiInstance`, and `TreeStepsMode`.
- `runAndCompareOptions`, `buildRunAndCompareOpts`, and `buildOptions` collect defaults, custom runs, standard options, random options, previous-run metadata, and initial state.
- `RunAndCompare` generates ops, writes the shared `ops` file, writes each run's `OPTIONS`, invokes child test processes in parallel, and compares histories.
- `RunOnce` is the child-run entry point. It reads `ops` and `OPTIONS`, parses them, configures FS/error injection/latency/initial state, initializes a `Test`, executes ops, and persists history.
- `Execute` replays operations serially or across goroutines using receiver-based hashing and `opsWaitOn` dependencies.
- `Compare`, `CompareHistories`, `lineByLineDiff`, `hashThread`, `readFile`, and `TestingT` support comparison and testing integration.

## Control Flow and State
`RunAndCompare` chooses a seed, creates a timestamped meta directory, chooses an op count and preset config, optionally loads prior ops through `loadPrecedingKeys`, generates formatted ops, and writes them once for all child runs. It builds a deterministic list of standard, custom, and random option names, then starts one child process per option under an `execution` subtest. Each child re-enters the top-level test with `--run-dir` pointing at its run directory.

After executions finish, `RunAndCompare` compares every history against the first option's history after comment stripping and operation reordering. On divergence it prints seed, focused diff, option strings, ops path, and a reduction command before exiting.

`RunOnce` does the actual replay. It parses serialized options into `defaultTestOptions`, wraps the configured filesystem with latency and injected read errors, handles tree-steps single-threading, bounds configured thread count, clones initial state if requested, fixes WAL failover/multi-instance incompatibilities, opens the history file, initializes `Test`, and executes. It prints LSM details for unclosed DBs and saves in-memory data on failure or keep mode.

`Execute` serially steps when `Threads <= 1`; otherwise each goroutine owns operations whose receiver hashes to its thread and waits on dependency channels computed by `newTest`/`computeDerivedFields`.

## State and Persistence Behavior
The harness writes a meta directory containing `ops`, one run directory per option, each run's `OPTIONS`, histories, data directories, optional runtime traces, and kept in-memory FS snapshots. It removes the meta directory after success unless `KeepData` is set. Initial-state extension copies prior persisted data and uses previous ops to seed interesting keys.

## Dependencies and Integration Points
This file integrates every other assigned file: `generator.go` for ops, `options.go` for test options, `ops.go` for replay, `history.go` for recording/comparison, and `key_manager.go` for preceding-key load. It also depends on parser support, `Test` construction/execution helpers, Pebble VFS/errorfs, randvar distributions, `errgroup`, and Go test subprocess behavior.

## Risks and Edge Cases
- Child process failures are reported with truncated history tail, but `os.Exit(1)` in compare paths bypasses normal `testing.T` cleanup.
- Multi-instance mode disables or adjusts WAL-related behavior and uses a restricted preset config.
- Error injection wraps read operations and must be paired with op retry behavior to avoid false divergences.
- History comparison ignores logger comment lines, so only recorded op outcomes participate in equality.
- `RunOnce` exits the process on replay error, which is appropriate for child mode but important for callers.

## Test Signals
This file is primarily covered by package-level metamorphic tests and options tests. `history_test.go` covers comparison primitives; `options_test.go` exercises `RunOnce` in `TestBlockPropertiesParse`; generator/key-manager tests cover operation construction used by `RunAndCompare`.
