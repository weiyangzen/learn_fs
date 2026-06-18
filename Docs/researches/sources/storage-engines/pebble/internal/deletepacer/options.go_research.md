# sources/storage-engines/pebble/internal/deletepacer/options.go

## Purpose
`options.go` defines runtime configuration for the delete pacer: the baseline deletion throughput, backlog drain horizon, and free-space reclaim threshold/horizon.

## Important APIs, Types, And Functions
`Options` exposes `BaselineRate func() uint64`, `BacklogTimeframe`, `FreeSpaceThresholdBytes`, and `FreeSpaceTimeframe`. `EnsureDefaults` installs a zero baseline function, a 5 minute backlog timeframe, a 16 GiB free-space threshold, and a 10 second free-space timeframe when fields are unset.

## Control Flow
Callers pass `Options` to `Open`, which calls `EnsureDefaults` before using them. The dynamic `BaselineRate` closure is intentionally evaluated by the rate calculator, allowing settings changes without reopening the pacer.

## State And Persistence Behavior
Options are process-local configuration. A zero baseline disables pacing. Timeframes and thresholds do not mutate after defaults are applied, but `BaselineRate` can return changing values.

## Dependencies And Integration Points
The options feed `rateCalculator.Update` and delete pacer queue scheduling. They are used directly by tests to exercise baseline changes, backlog acceleration, free-space acceleration, and close-time pacing disablement.

## Risks And Edge Cases
Zero values mean defaults except for baseline, where zero means disabled pacing. Very small timeframes can create aggressive rates; nil `BaselineRate` is safe after defaults. The defaults assume local disk reclamation semantics and may be unsuitable for unusual deployment storage.

## Test Signals
`rate_calc_test.go` validates how options influence computed rates. `delete_pacer_test.go` validates end-to-end pacing behavior with default and overridden thresholds.
