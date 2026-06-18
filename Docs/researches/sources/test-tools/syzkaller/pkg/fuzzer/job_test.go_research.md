# sources/test-tools/syzkaller/pkg/fuzzer/job_test.go

## Purpose
This file tests `triageJob.deflake`, especially how repeated executions are merged into stable signal and coverage.

## Important APIs, Types, And Functions
`TestDeflake` defines table-driven cases with initial `triageCall` state, an execution callback returning errno/signal/cover per run, and expected run count. It builds a minimal test target/program, creates a `triageJob` with `newCover` and empty config, and invokes `deflake` through a fake executor callback.

## Control Flow
Each case resets derived fields, seeds `signals[0]` from new signal, and calls `deflake`. The fake callback increments run count and returns a `queue.Result` with one `flatrpc.CallInfo`. Assertions compare whether deflake stopped normally, how many runs were used, and whether cover/stable/new-stable signal match expectations.

## State And Persistence Behavior
State is in-memory test data. It verifies that coverage is unioned across runs and that stable signal uses the required-run intersection logic. One case includes a differing errno comment, although the visible fake result still supplies call info directly to deflake.

## Dependencies And Integration Points
The test depends on `cover`, `signal`, `flatrpc`, `queue`, `prog`, `targets`, and `testify/assert`. It validates the core triage policy used before corpus insertion.

## Risks
The test focuses on single-call behavior and does not cover minimization, corpus saving, hints, fault injection, snapshot stopping, corpus-specific stopping, or executor stop statuses.

## Test Signals
Expected signals include empty stable output after fully flaky runs, unioned coverage, and new stable signal intersection. The run-count assertions guard deflake stopping conditions.
