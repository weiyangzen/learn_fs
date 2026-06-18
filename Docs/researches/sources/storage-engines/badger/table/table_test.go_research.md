# sources/storage-engines/badger/table/table_test.go

## Purpose
This file provides broad tests and benchmarks for SSTable reading, iteration, concatenation, merge behavior with real tables, checksum validation, large values, bloom filters, race-sensitive lookup, and max-version metadata.

## Important Tests and Helpers
- `getTestTableOptions`, `buildTestTable`, and `buildTable` create sorted test SSTables.
- `TestTableIterator`, `TestSeekToFirst`, `TestSeekToLast`, `TestSeek`, `TestSeekForPrev`, `TestIterateFromStart`, `TestIterateFromEnd`, `TestTable`, `TestIterateBackAndForth`, and `TestUniIterator` validate table iterator navigation.
- `TestConcatIteratorOneTable` and `TestConcatIterator` validate ordered table concatenation forward and reverse.
- `TestMergingIterator`, reversed variants, and take-one/take-two cases test merge iterator behavior with actual table iterators.
- `TestTableBigValues`, `TestTableChecksum`, `TestDoesNotHaveRace`, and `TestMaxVersion` cover storage edge cases.
- Benchmarks measure full scans, read-and-build, merged reads, checksum algorithms, and random reads.

## Control Flow and State Behavior
The helper sorts input key/value pairs, adds timestamped keys to a builder, creates an SSTable in the temp directory, and returns an open table whose ref must be decremented. Iterator tests position internal or public iterators, then compare parsed user keys and decoded values. Concat and merge tests compose table iterators to validate cross-table ordering and duplicate winner behavior.

Checksum testing deliberately corrupts table mmap bytes after building with checksum verification enabled and expects open/verification to panic or fail with checksum evidence. The race test concurrently calls `DoesNotHave` to exercise bloom/index access.

## Dependencies and Integration Points
The tests depend on `table.Builder`, `Table`, `Iterator`, `ConcatIterator`, `MergeIterator`, Badger `options`, `y` helpers, Ristretto cache, and standard hashing libraries for benchmarks.

## Risks and Edge Cases
Tests use temp files and rely on `DecrRef` for cleanup. Some benchmarks contain performance-only paths and are not routine correctness gates. `TestTableChecksum` mutates mmap data directly and accepts either panic or checksum error, reflecting multiple possible corruption detection points.

## Test Signals
The suite strongly validates iterator boundary behavior, block crossing, reverse traversal, concat range selection, duplicate merge behavior, corruption detection, big value decoding, bloom filter concurrency, and `MaxVersion` metadata.
