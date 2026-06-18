# sources/storage-engines/pebble/mem_table_test.go

Purpose: this file tests and benchmarks memtable behavior, including basic point operations, iteration bounds, range deletion fragmentation, concurrent tombstone cache invalidation, memory reservation, overlap computation, and iterator performance.

Important APIs/types/functions: helper methods `memTable.get`, `memTable.set`, `memTable.count`, and `ikey` simplify direct test access. Unit tests include `TestMemTableBasic`, `TestMemTableCount`, `TestMemTableEmpty`, `TestMemTable1000Entries`, `TestMemTableIter`, `TestMemTableDeleteRange`, `TestMemTableConcurrentDeleteRange`, `TestMemTableReserved`, and datadriven `TestMemTable`. `buildMemTable` and benchmark functions cover seek, bounded seek, successive seek, next, and prev workloads.

Control flow: basic tests insert keys directly and read through skiplist iterators. Datadriven iterator tests define internal keys and delegate operations to `itertest.RunInternalIterCmd`. Range-delete tests apply batches with monotonically increasing sequence numbers, then scan either point keys or range-delete spans. The concurrent range-delete test launches workers that repeatedly apply non-overlapping tombstones and immediately verify their own span counts through `newRangeDelIter`. Reservation tests call `prepare` without apply to verify pessimistic accounting.

State and persistence behavior: tests allocate memtables in process memory and close batches/iterators where needed. Concurrent tests exercise atomic cache invalidation and lazy fragmentation under write/read races. Benchmarks fill a memtable until arena full, then reuse iterators within the benchmark loop.

Dependencies and integration points: uses datadriven fixtures, batch definition helpers, `itertest`, `arenaskl`, range-key helpers, errgroup concurrency, random generators, and testify requirements. Benchmarks simulate workloads relevant to CockroachDB bounded scans and iterator movement.

Risks and test signals: direct `set` bypasses prepare/apply and is intentionally caveated, so some tests focus on skiplist semantics rather than commit-pipeline semantics. Strong signals include concurrent range tombstone cache correctness, memory accounting after prepare, bounds behavior, and performance regressions in common iterator operations.
