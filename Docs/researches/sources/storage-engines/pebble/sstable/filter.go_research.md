# sources/storage-engines/pebble/sstable/filter.go

## Purpose
Defines table filter metrics and a small reader wrapper that records filter hits and misses.

## Important APIs, Types, and Functions
- `FilterMetrics` exposes hit/miss counters.
- `FilterMetricsTracker` stores atomic hit/miss counters and has `Load`.
- `tableFilterReader` pairs a `base.TableFilterDecoder` with optional metrics.
- `newTableFilterReader` constructs the wrapper.
- `mayContain` invokes the decoder and updates metrics.

## Control Flow
`mayContain` calls `decoder.MayContain(data, key)`. If metrics are configured, a false result increments hits because the filter avoided a data-block access, while a true result increments misses because the filter could not rule out the key.

## State and Persistence Behavior
No on-disk persistence. Metrics live in atomics and can be loaded safely while readers run.

## Dependencies and Integration Points
Used by SSTable readers with table filter blocks, including bloom/binary fuse decoders. `ReaderOptions.FilterMetricsTracker` supplies the metrics sink.

## Risks and Edge Cases
Metric naming is easy to invert: “hit” means a successful negative filter result. Unsupported filter families are handled elsewhere by not constructing a reader.

## Test Signals
Indirectly exercised by filter/reader tests and datadriven iterator tests that use filter policies.
