## sources/user-network-fs/gcsfuse/benchmarks/internal/percentile/duration_test.go

Purpose: Unit tests for percentile duration interpolation.

Important APIs/types/functions: `TestDuration` runs ogletest suites. `DurationTest` methods `OneObservation`, `TwoObservations`, `ThreeObservations`, and `FiveObservations` define sorted values and expected percentiles.

Control flow: each test iterates table cases and checks `percentile.Duration(vals, p)` with `ExpectEq`.

State and persistence: no persistent state.

Dependencies and integration points: imports `github.com/jacobsa/ogletest` and the internal percentile package.

Risks: tests cover valid sorted input only; they do not document panic behavior for empty/out-of-range/unsorted input.

Test signals: strong signal for Excel-style interpolation expectations at common percentile values.
