<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/latency.go -->
# sources/storage-engines/pebble/vfs/errorfs/latency.go

## Purpose
Adds latency injection to `errorfs` without returning errors. It is used to deterministically simulate slow IO operations, especially in WAL failover monitoring tests.

## Important APIs, Types, and Functions
`RandomLatency` constructs an `Injector` that sleeps for an exponentially distributed duration when an optional predicate matches. `parseRandomLatency` registers the DSL form. `randomLatency.MaybeError` performs the sleep and always returns nil. `keyedPrng` provides path-keyed deterministic PRNG state shared with random predicates.

## Control Flow
`RandomLatency` initializes a `randomLatency` with predicate, mean, optional total limit, and seeded `keyedPrng`. `MaybeError` checks the predicate, derives a per-path random duration capped at 20 times the mean, optionally caps aggregate injected latency with an atomic counter, sleeps, and returns nil. `parseRandomLatency` consumes a duration string, seed, optional predicate, and closing parenthesis.

## State and Persistence Behavior
State is entirely in memory. `randomLatency.agg` tracks total injected sleep time if a limit is configured. `keyedPrng` lazily creates and caches a `rand.Rand` per key under a mutex; this makes results deterministic per file path across interleavings that touch different paths.

## Dependencies and Integration Points
Depends on `internal/dsl`, `math/rand/v2`, `hash/maphash`, and `time`. Registered from `NewParser` in `dsl.go` as `RandomLatency`. WAL failover tests wrap VFSs with random latency injectors to make monitor/prober switching paths observable.

## Risks and Edge Cases
The path-keyed PRNG serializes access under a mutex, which is fine for tests but not intended as a hot production path. Latency is capped to avoid extreme test timeouts, changing the tail of the exponential distribution. Aggregate limit accounting can overshoot then cap the final sleep, but once already over limit it injects nothing.

## Test Signals
`errorfs_test.go` covers parsing and string rendering. `failover_manager_test.go` uses `RandomLatency` with `Randomly` to drive quiesce and all-files-deletable tests under delayed operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/latency.go -->
