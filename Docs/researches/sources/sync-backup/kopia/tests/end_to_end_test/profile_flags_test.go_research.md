# sources/sync-backup/kopia/tests/end_to_end_test/profile_flags_test.go

## Purpose
Tests diagnostics/profile CLI flags produce expected pprof files.

## Important APIs, Types, and Functions
`TestProfileFlags` uses an external executable runner, diagnostics output directory, and repo status profile flags.

## Control Flow
The test creates a repo, runs `repo status` with diagnostics directory and CPU/block/mutex/memory profiling options, locates the per-execution `profiles` directory, and asserts seven profile files exist and are non-empty.

## State and Persistence Behavior
Writes diagnostics artifacts to a temp directory. Repository state is otherwise incidental.

## Dependencies and Integration Points
Exercises CLI profiling setup/teardown, diagnostics directory layout, pprof profile writers, and executable-runner path.

## Risks
Uses `NewExeRunner`, so it depends on a built binary rather than in-process execution. Profile file names and layout are part of the test contract.

## Test Signals
Confirms CPU, allocs, block, goroutine, mutex, heap, and threadcreate profiles are emitted on command exit.
