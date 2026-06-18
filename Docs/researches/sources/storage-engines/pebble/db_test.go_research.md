# sources/storage-engines/pebble/db_test.go

## Purpose
`db_test.go` is a broad behavioral and regression suite for Pebble's core DB implementation. It validates the public read/write API, batch application, WAL and memtable rotation, flushing, compaction, close-time cleanup, iterator and memtable reference accounting, SSTable introspection, tracing, WAL failover, determinism under reordered execution, and read concurrency limiting.

## Important APIs, types, and functions
`try` is a test helper that retries a condition with exponential backoff. `verifyGet` and `verifyGetNotFound` centralize `Reader.Get` assertions. The main tests exercise `Open`, `Set`, `Delete`, `SingleDelete`, `Merge`, `LogData`, `Apply`, `Flush`, `AsyncFlush`, `Compact`, `Ingest`, `Excise`, `SSTables`, `NewIter`, `NewSnapshot`, `NewBatch`, `NewIndexedBatch`, `Metrics`, and `Close`.

Test-only helper types include `closableMerger`, which verifies that merge value closers are propagated; `testTracer`, which records tracing events; `sstAndLogFileBlockingFS`, which blocks WAL or SST creation to force stall/failover scenarios; `testLogManager`, which can dynamically elevate write-stall thresholds; ordering tree types (`sequential`, `reorder`, `parallel`, `leaf`) for deterministic reruns; and `readTrackFS`/`readTrackFile`, which count concurrent SST reads for semaphore enforcement.

## Control flow, state, and persistence
The early tests validate basic persisted state by opening staged testdata directories, applying direct and batched writes, and comparing reads against an expected in-memory map. Random write tests force memtable churn with small memtables. `TestLargeBatch` validates the special large-batch path: a value larger than the configured threshold is written to the pre-existing WAL, triggers WAL rotation, leaves the new WAL empty, and eventually produces the expected L0 files.

Merge and SingleDelete tests validate subtle internal-key semantics across memtables and flushes, including a snapshot case where an older value must remain visible to a snapshot while the DB observes deletion. Leak tests intentionally leave iterators or memtable refs open and require `Close` to report leaked versions or reservations. Manifest tests force frequent MANIFEST rollover, check the current descriptor, and verify preservation of the configured number of previous manifests. Close tests assert that closed DB operations panic with `ErrClosed`.

Concurrency tests stress `Set`, `Compact`, `Flush`, and `AsyncFlush` in parallel, close while compactions are active, and race file cleaning with DB close. SSTable tests validate property loading, key-range filtering, approximate span-byte estimation, and virtual SSTable metadata after excise. Tracing is datadriven and covers gets plus iterators over DB, snapshot, and indexed-batch views. `TestMemtableIngestInversion` constructs a complex sequence of blocked compactions, blocked flushes, ingests, range deletes, and memtable writes to guard against a historical L0 sublevel/sequence-number inversion bug.

The WAL failover tests use blocking filesystems and a fake log manager to ensure write stalls are avoided or unblocked when failover elevation applies. `TestDeterminism` records a datadriven sequence and reruns it under sequential, reordered, parallel, and latency-injected schedules to ensure output stability. `TestLoadBlockSema` confirms `LoadBlockSema` bounds concurrent SST reads during parallel `Get` workloads.

## Dependencies and integration points
The tests use `vfs.NewMem`, `errorfs`, `wal`, `sstable`, `objstorageprovider`, `cache`, `testkeys`, `testutils`, `datadriven`, `leaktest`, `require`, and numerous Pebble test helpers from other files such as `runBatchDefineCmd`, `runBuildCmd`, `runCompactCmd`, `runDBDefineCmd`, `runExciseCmd`, and ingestion helpers. They intentionally reach into `d.mu`, version metadata, WAL manager internals, and metrics, so they are package-level tests tightly coupled to core internals.

## Risks and invariants
Because these tests inspect internal strings, file numbers, and version layouts, they can be sensitive to legitimate compaction, manifest, or formatting changes. Several tests rely on timing, blocking filesystems, or background scheduling; they include timeouts and semaphores, but slow or highly contended environments could expose flakes. The determinism harness is powerful but only covers operations expressed in its datadriven command set. Tests that accept randomized options must account for option-dependent behavior.

## Test signals
This file itself is the test signal for `db.go` and related components. Its benchmarks also signal performance-sensitive areas: delete versus single-delete, iterator construction and close cost under high read amplification, and repeated memtable rotation for large memtables.
