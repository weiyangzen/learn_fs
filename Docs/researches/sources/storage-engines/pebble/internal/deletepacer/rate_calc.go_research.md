# sources/storage-engines/pebble/internal/deletepacer/rate_calc.go

## Purpose
`rate_calc.go` calculates the delete pacer’s target bytes/sec and pacing debt. It combines a baseline rate, recent deletion feed-forward, backlog drain pressure, and low-free-space pressure.

## Important APIs, Types, And Functions
`rateCalculator` holds options, a disk-free-space callback, `lastUpdate`, `currentRate`, `debtBytes`, `backlogRate`, and `freeSpaceRate`. `makeRateCalculator` initializes it. `Update(now, recentPacingBytes, queuedPacingBytes, disablePacing)` recalculates rate and decays debt. `AddDebt(bytes)` records bytes for a started deletion with a 1 GiB cap. `InDebt` and `DebtWaitTime` expose whether and how long to wait.

## Control Flow
`Update` first computes elapsed time and reads the baseline. If baseline is zero or pacing is disabled, all rate/debt state is cleared. Otherwise it decays debt by the previous current rate, sets the base current rate to max(baseline, recent bytes over `RecentRateWindow`), raises `backlogRate` when queued bytes exceed recent bytes, raises `freeSpaceRate` when disk free space is under threshold, and adds the larger corrective component. `DebtWaitTime` divides debt by current rate and rounds up by 1ns.

## State And Persistence Behavior
All state is in-memory and monotonic-time based. Backlog and free-space corrective rates are sticky upward until their condition clears, implementing a constant-horizon drain model. Debt represents already initiated deletion work and decays over updates.

## Dependencies And Integration Points
It depends on deletepacer `Options`, `DiskFreeSpaceFn`, `RecentRateWindow`, `crtime.Mono`, and `cockroachdb/errors`. The main delete loop calls it before deletes and after enqueue changes.

## Risks And Edge Cases
The calculator assumes callers call `Update` often enough for debt decay. `DebtWaitTime` panics on zero debt and assumes `currentRate > 0`; it should only be called after `InDebt` in paced mode. The 1 GiB debt cap intentionally trades precise pacing for avoiding excessive stalls on huge files.

## Test Signals
`rate_calc_test.go` is the direct test suite, with datadriven simulations covering baseline changes, backlog, free-space deficits, disabled pacing, debt accumulation, and wait-time formatting.
