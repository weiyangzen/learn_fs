# sources/storage-engines/pebble/internal/batchskl/skl_test.go

Purpose: Tests and benchmarks the batch skiplist and iterator.

APIs and types: Exercises `Skiplist`, `Iterator`, `ErrTooManyRecords`, `NewIter`, `Add`, `SeekGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, and bounds handling.

Control flow and state: Test storage encodes batch records, inserts ordered and unordered keys, checks forward/reverse lengths, verifies duplicate/newer ordering, forces overflow, and validates bound semantics. Benchmarks measure random and ordered writes plus iteration.

Persistence and dependencies: Uses in-memory encoded batch records only. Depends on base comparer, rand, errors, and testify.

Integration points: Protects batch indexing behavior used by write batch readers and indexed batches.

Risks: TODO notes missing dedicated tests for `First` and `Last`; they are still touched by length helpers and benchmarks.

Test signals: Strong local coverage for skiplist mechanics, seek correctness, bounds, and performance-sensitive paths.
