<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metrics_test.go -->
## sources/storage-engines/pebble/metrics_test.go

Purpose: validates Pebble metrics formatting, metric values under DB operations, and several metric regressions.

Important APIs and functions: `exampleMetrics` constructs a populated `Metrics` snapshot for golden output. `TestMetrics` is datadriven over `testdata/metrics` with commands for DB initialization, batches, building SSTs, compaction, delayed flush state, flush, ingest, LSM dump, iterator open/close, metric rendering, metric value extraction, disk usage, additional block-write metrics, and problem spans. Regression tests cover remote table totals with virtual SSTables, write amp with WAL disabled, WAL bytes written monotonicity, and cumulative flushable memory bytes.

Control flow: `TestMetrics` opens DBs over MemFS with deterministic options, optional shared storage, value separation enabled, automatic compactions disabled, and high `MaxOpenFiles`. It waits for table stats before reading metrics, zeroes known nondeterministic cache/delete-pacer fields when commanded, and compares formatted output. Regression tests build focused DB states and assert exact invariants.

State and persistence: uses in-memory FS and remote storage, but exercises real Pebble state transitions: writes, flushes, compactions, ingests, virtual tables, iterators pinning obsolete files, and reopen stats loading.

Dependencies and integration: integrates metrics with DB operations, object storage provider, remote storage, vfs/errorfs latency injection, cache, delete pacer, block categories, testkeys comparer, and datadriven fixtures.

Risks and edge cases: golden metrics output can be brittle across architecture, timing, and reader-size changes; `StringForTests` normalizes several fields. The monotonic WAL test is time-bound and concurrency-sensitive.

Test signals: this is the primary behavioral signal for `metrics.go`, including redaction equivalence, remote virtual-table underflow regression, WAL monotonicity, and flushable memory accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metrics_test.go -->
