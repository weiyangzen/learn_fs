# sources/storage-engines/pebble/internal/deletepacer/rate_calc_test.go

## Purpose
`rate_calc_test.go` provides datadriven tests for `rateCalculator`, making rate and debt transitions visible with human-readable byte/sec and byte values.

## Important APIs, Types, And Functions
`TestRateCalculatorDataDriven` runs `testdata/rate-calc`. `runSimulation` parses command arguments into `testConfig`, constructs `Options`, creates a `rateCalculator`, executes scripted lines, and writes formatted state lines. Constants `MB` and `GB` are shared with deletepacer tests.

## Control Flow
The parser supports setup arguments such as `baseline-rate`, `free-space-threshold`, `free-space-timeframe`, `backlog-timeframe`, and `disk-free-space`. Input commands mutate state (`set-baseline-rate`, `set-free-space`, `add-debt`) or call `Update` at an absolute monotonic timestamp with `recent=`, `queued=`, and optional `disable-pacing`. Output reports rounded current rate, backlog/free-space components, debt, and rounded wait time.

## State And Persistence Behavior
Test state is purely in-memory. Time is synthetic `crtime.Mono`, which makes debt decay deterministic. The datadriven file is the persistent expected behavior.

## Dependencies And Integration Points
It uses `datadriven`, `crhumanize`, `crstrings`, `crtime`, `math.Round`, and `testify/require`. It directly tests unexported deletepacer internals because it is in package `deletepacer`.

## Risks And Edge Cases
Rounding to integer bytes/sec and whole-second wait times can hide tiny numerical differences but makes golden output stable. Because command time is absolute, out-of-order timestamps would create negative elapsed time and are not explicitly rejected.

## Test Signals
The golden file detects regressions in feed-forward rate, constant-horizon backlog/free-space rate stickiness, zero-baseline pacing disablement, debt cap/decay, and wait-time calculation.
