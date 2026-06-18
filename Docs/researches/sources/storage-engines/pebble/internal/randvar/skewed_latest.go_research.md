<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/skewed_latest.go -->
# sources/storage-engines/pebble/internal/randvar/skewed_latest.go

Purpose: dynamic random variable that returns values in `[min,max]` skewed toward the latest/highest values using a Zipf distribution over distance from max.

Important APIs/types: `SkewedLatest`, `NewDefaultSkewedLatest`, `NewSkewedLatest`, `IncMax`, `Max`, and `Uint64`.

Control flow and state: construction stores `max` and creates a `Zipf` over `[0, max-min]`. `Uint64` locks for reading, draws a Zipfian distance, and returns `max - distance`, so recent high values are favored. `IncMax` locks for writing, expands the underlying Zipf max by `delta`, and increments current max. `Max` reads the current max under lock.

Persistence and integration: state is in-memory and concurrency-protected. Used by `randvar.Flag` for `latest:` specs and randomized workloads. Risks include dependence on `Zipf` implementation not shown here, nil RNG handling delegated to `Zipf.Uint64`, and no direct storage of `min` beyond the initial Zipf range. Tests check max changes and range bounds after increment.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/skewed_latest.go -->
