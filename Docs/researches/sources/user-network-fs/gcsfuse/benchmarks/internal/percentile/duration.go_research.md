## sources/user-network-fs/gcsfuse/benchmarks/internal/percentile/duration.go

Purpose: Provides duration sorting and percentile calculation for benchmark latency summaries.

Important APIs/types/functions: `DurationSlice []time.Duration` implements `sort.Interface`. `Duration(vals DurationSlice, p int) time.Duration` computes the pth percentile by Excel-style linear interpolation.

Control flow: assumes sorted non-empty values and `0 <= p <= 100`; computes rank `(p/100)*(N-1)`, splits integer/fractional parts with `math.Modf`, interpolates between adjacent observations or returns the last observation, otherwise panics.

State and persistence: stateless; does not sort internally.

Dependencies and integration points: benchmark programs sort `DurationSlice` then call `Duration` for p50/p90/p98 style reports.

Risks: preconditions are unchecked except final panic; empty, unsorted, or out-of-range inputs yield wrong results or panic. Float conversion of durations is fine for benchmark ranges but can lose precision near extremes.

Test signals: `duration_test.go` covers one, two, three, and five observations with multiple percentile points.
