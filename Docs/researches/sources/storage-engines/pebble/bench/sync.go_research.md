# sources/storage-engines/pebble/bench/sync.go

## Purpose
`sync.go` implements a write/fsync latency benchmark. It can either write real key/value records or WAL-only `LogData` records, measuring operation latency and MB/sec.

## Important APIs, Types, And Functions
`SyncConfig`, `DefaultSyncConfig`, and `RunSync` are the public surfaces. Config controls batch-size distribution, WAL-only mode, and value-size distribution.

## Control Flow
`RunSync` creates a histogram registry and byte counter, selects `pebble.Sync` or `NoSync`, and runs workers through `RunTest`. Each worker repeatedly waits on the limiter, creates a batch, generates `count` values, appends either `LogData` or MVCC-encoded `Set` records, commits, records latency, and adds byte totals. Tick/done callbacks report op rate, MB/sec, and latency percentiles.

## State And Persistence Behavior
In normal mode it writes random MVCC keys to Pebble. In WAL-only mode it persists only WAL records that do not enter memtables or sstables. Sync mode stresses durable WAL fsync unless disabled by config.

## Dependencies And Integration Points
It uses `pebble`, `cockroachkvs`, `randvar`, `histogramRegistry`, `RunTest`, and rate limiting from `CommonConfig`.

## Risks And Edge Cases
The workload is unbounded until harness termination. Random keys may overwrite occasionally but are intended as broad write load. `DisableWAL` changes benchmark semantics significantly. Fatal errors stop the process.

## Test Signals
No direct tests. Output histograms and Pebble metrics are used for manual/benchmark validation.
