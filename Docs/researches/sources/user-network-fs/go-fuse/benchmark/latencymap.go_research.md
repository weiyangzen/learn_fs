# sources/user-network-fs/go-fuse/benchmark/latencymap.go

Purpose: concurrency-safe accumulator for benchmark latency counts and durations by operation name.

Important APIs/types: `LatencyMap` embeds `sync.Mutex` and holds `map[string]*latencyMapEntry`; `NewLatencyMap` initializes the map; `Add` increments count and total duration; `Get` returns count and duration; `Counts` returns a copy of operation counts.

Control flow/state: all map access is mutex-protected. `Get` releases the lock before checking the copied pointer, which is safe for nil detection but reads `count`/`dur` after unlock; concurrent `Add` may race under the Go race detector because the entry fields are mutable. A safer implementation would copy values while locked.

Dependencies/integration: used by benchmark/instrumented examples. Test signal in `latencymap_test.go` covers simple accumulation but not concurrency.
