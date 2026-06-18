# sources/storage-engines/pebble/sstable/suffix_rewriter_test.go

## Purpose
Tests and benchmarks SSTable suffix rewriting across table formats, property collectors, filters, point keys, and range keys.

## Important APIs, Types, And Functions
`TestRewriteSuffixProps` is the main correctness test. `makeTestkeySSTable` builds synthetic SSTables with a shared prefix, test-key suffixes, point SETs, and range-key SETs. `BenchmarkRewriteSST` compares `RewriteKeySuffixesViaWriter` with block-level rewriting at several concurrency levels.

## Control Flow And State
The test iterates table formats from Pebblev2 through `TableFormatMax`, creates an SSTable with a random subset of test block property collectors, then rewrites suffix `@212` to `@645` using both the by-block and writer-loop paths. Rewriter options intentionally specify a random table format to verify that block-level rewrite preserves the original format. New collector subsets are shuffled and truncated, then expected table and block property values are checked on the rewritten reader. Each rewrite is repeated five times to catch mutation of the source SSTable buffer.

`makeTestkeySSTable` writes many point keys through `Raw().Add` and range keys through `RangeKeySet`. The benchmark constructs SSTables at 100, 10,000, and 1,000,000 keys with no compression and Snappy, then measures reader/writer loop and block rewrite with concurrency 1, 2, 4, 8, and 16.

## Persistence And Integration
Tests use `objstorage.MemObj` and `NewMemReader` for in-memory SSTables. They integrate with test key comparers/schemas, Bloom filters, block property collector test utilities, range keys, table layout inspection, and reader property loading.

## Risks
The test uses random collector subsets and seeds are logged, which helps reproduction. It focuses on suffix-rewrite-compatible SSTables and does not test expected failures like bad suffixes, non-SET point keys, value-block SSTables, mismatched comparers, or unsupported collectors. The benchmark appears to pass `_123`/`_456` in one block-rewrite branch while constructed keys use `@123`/`@456`, which may be intentional failure-path coverage or a typo worth reviewing if the benchmark is used.

## Test Signals
Strong signal for successful suffix rewrite metadata behavior: table properties, user property short IDs, per-block properties, format preservation, filter copy viability, and by-block versus reader/writer equivalence when block boundaries are unchanged.
