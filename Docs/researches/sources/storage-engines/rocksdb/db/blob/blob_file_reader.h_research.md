<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_reader.h

## Purpose
Declares `BlobFileReader`, the random-access reader for RocksDB blob log files. It exposes single-blob and batched blob retrieval while hiding file open, format validation, direct I/O, decompression, and footerless direct-write handling.

## Important APIs, Types, and Functions
The overloaded static `Create` factory has a normal path and a `skip_footer_validation` path for in-flight direct-write blob files. `GetBlob` reads one blob by user key, value offset, stored size, and compression type. `MultiGetBlob` accepts sorted `BlobReadRequest` entries and fills per-request status/content pairs. `GetCompressionType` and `GetFileSize` expose file metadata for callers. Private helpers perform open, header/footer reads, raw reads, blob verification, and decompression.

## Control Flow
Callers construct readers through `Create`, then issue reads against BlobIndex-derived offsets. The read path can validate only byte ranges or the full record depending on `ReadOptions::verify_checksums`. Batched callers must sort offsets ascending before calling `MultiGetBlob`, enabling efficient filesystem multi-read.

## State and Persistence Behavior
Reader state is immutable after construction: owned file reader, file size, compression type, decompressor, clock/statistics pointers, and whether the footer was present when opened. It does not persist changes; it only reports counters and returns allocated `BlobContents`.

## Dependencies and Integration Points
The header exposes dependencies on `BlobReadRequest`, `RandomAccessFileReader`, advanced compression, file prefetching, memory allocators, RocksDB read/file/immutable options, and statistics. It is consumed by blob cache/source code, version blob reads, direct-write fallback, compaction blob reads, and tests.

## Risks and Edge Cases
The footer-skipping factory is intentionally special-purpose; using it on ordinary manifest-visible files would reduce corruption detection. `MultiGetBlob` requires sorted offsets and a batch size bounded by `MultiGetContext::MAX_BATCH_SIZE`. Callers must pass the same compression type and logical user key used when the blob record was written, especially when checksums are verified.

## Test Signals
The associated test file validates factory behavior, direct/read paths, corruption handling, compression, I/O propagation, and multiget edge cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader.h -->
