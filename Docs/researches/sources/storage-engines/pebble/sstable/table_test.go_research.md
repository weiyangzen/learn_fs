# sources/storage-engines/pebble/sstable/table_test.go

## Purpose
Provides broad SSTable reader/writer regression coverage over prebuilt Hamlet fixture tables and freshly generated in-memory tables. It verifies point lookup, forward/backward iteration, bounds, Bloom/table filter behavior, final block flushing, synthetic sequence numbers, metaindex ordering, and footer decoding across table formats/checksum types.

## Important APIs, Types, And Functions
`check` opens a `Reader`, validates `get`, `NewIter`, `SeekGE`, `SeekLT`, `First`, `Last`, bounds, and missing-key behavior. `testReader` drives prebuilt fixtures. `countingFilterDecoder` wraps the Bloom decoder and classifies true/false positives/negatives. Tests include `TestReaderDefaultCompression`, `TestReaderNoCompression`, `TestReaderTableBloom`, `TestReaderBloomUsed`, `TestBloomFilterFalsePositiveRate`, `TestWriterRoundTrip`, `TestFinalBlockIsWritten`, `TestReaderSymtheticSeqNum`, `TestMetaIndexEntriesSorted`, `TestFooterRoundTrip`, and `TestReadFooter`.

## Control Flow
Most tests construct or open an SST, create a `Reader`, and exercise public/internal iterator APIs over the same expected Hamlet word-count data. Bloom tests replace the decoder with a counting shim. Writer round trips vary block and index sizes, optionally attach a Bloom policy, close the writer, reopen the file, and reuse `check`. Footer tests encode synthetic footers into arbitrary offsets, read them back, and exercise malformed encodings.

## State And Persistence Behavior
The file persists test SSTs in memory for generated cases and reads durable prebuilt fixtures from `testdata`. It validates physical table state through reopened readers, metaindex block contents, block flush completion, and footer handles. It does not mutate production DB state.

## Dependencies And Integration Points
Depends on `Reader`, `newReader`, `Writer`, `NewRawWriter`, `objstorageprovider`, block compression/checksum code, Bloom filter decoders, row-block raw iterators, VFS implementations, and fixture helpers in `test_fixtures.go`. The tests indirectly cover table format compatibility and reader integration with filter policies.

## Risks And Edge Cases
Important risks covered are final partial block loss, out-of-bounds iterator behavior, false-negative filters, degenerate filters that always return true, malformed footers with table-number context, and metaindex key ordering. The Hamlet data is fixed, so coverage is deterministic but not exhaustive for newer columnar-format features.

## Test Signals
Signals are exact key/value equality, expected ErrNotFound, bounded iteration counts, Bloom false-positive ratios, byte counts after reopening, sorted metaindex keys, footer round-trip equality, and expected error substrings for corrupt footers.
