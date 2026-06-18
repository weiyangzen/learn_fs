# sources/storage-engines/pebble/internal/ewma/ewma_bytes_test.go

## Purpose
`ewma_bytes_test.go` validates the byte-based EWMA estimator’s intuitive behavior and numeric half-life accuracy.

## Important APIs, Types, And Functions
`TestBytes` covers initialization, NaN estimate before sampling, dominance of recent samples after large gaps, averaging of adjacent small blocks, and half-life weighting. `TestBytesHalfLife` iterates half-life values from 1 byte to 1 GiB and verifies `decay(n)` at 1x through 6x half-life.

## Control Flow
The tests build a `Bytes` estimator, call `SampledBlock` and `NoSample` in scripted sequences, and compare estimates using epsilon tolerances. Half-life subtests use `t.Run` with `fmt.Sprint(n)`.

## State And Persistence Behavior
All test state is local. `Init` is tested as a state reset. No persistent files or external resources are used.

## Dependencies And Integration Points
It depends on Go `math`, `testing`, `fmt`, and `testify/require`. It directly accesses unexported `decay` because the test is in package `ewma`.

## Risks And Edge Cases
The epsilon in `TestBytes` is intentionally loose for intuitive estimates, while the decay test uses tighter tolerance. It does not test invalid half-life or invalid sample sizes.

## Test Signals
Passing tests signal that the estimator handles large gaps without changing stale-only estimates, shifts strongly toward recent samples after decay, and preserves half-life math across very large byte windows.
