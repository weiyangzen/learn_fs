# sources/storage-engines/rocksdb/db/blob/blob_counting_iterator_test.cc

## Purpose
Unit tests for `BlobCountingIterator` and its integration with `BlobGarbageMeter`.

## Important Test Flow
`CountBlobs` builds a `VectorIterator` over two blob-index values and one plain value. It encodes blob references with different file numbers and sizes, computes expected bytes including blob log record header adjustment, and verifies inflow counts/bytes after `SeekToFirst`, `Next`, `NextAndGetResult`, `SeekToLast`, `Prev`, `Seek`, and `SeekForPrev`. `CheckInFlow` inspects `blob_garbage_meter.flows()` and handles absent entries as zero. `CorruptBlobIndex` uses an invalid blob-index payload and verifies the wrapper becomes invalid with non-OK status.

## Dependencies, Risks, and Test Signals
The tests depend on `BlobIndex`, `BlobLogRecord`, internal key encoding, and `VectorIterator`. They intentionally demonstrate that revisiting entries increments inflow again. The main risk under test is corruption propagation from `ProcessInFlow`. The file is itself the direct signal that counting behavior matches compaction accounting expectations.
