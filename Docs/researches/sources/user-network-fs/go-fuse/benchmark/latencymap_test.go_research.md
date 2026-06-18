# sources/user-network-fs/go-fuse/benchmark/latencymap_test.go

Purpose: validates basic `LatencyMap` accumulation semantics.

Important test flow: creates a map, calls `Add("foo", 100ms)` and `Add("foo", 200ms)`, then asserts `Get("foo")` returns count `2` and total duration `300ms`.

State/dependencies: uses no external state beyond Go test runtime and `time.Duration`.

Integration/risk coverage: confirms same-key aggregation but does not test missing keys, `Counts`, concurrent access, or data-race behavior. The error text says "want 2, 150ms" while the assertion expects `300ms`; this is a minor diagnostic mismatch that could confuse failure triage.
