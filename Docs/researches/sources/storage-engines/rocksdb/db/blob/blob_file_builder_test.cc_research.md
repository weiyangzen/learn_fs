# sources/storage-engines/rocksdb/db/blob/blob_file_builder_test.cc

## Purpose
Unit tests for `BlobFileBuilder` output files, blob indexes, metadata, compression, checksums, threshold inlining, and error paths.

## Important Test Flow
`BlobFileBuilderTest` uses `MockEnv`, a deterministic file-number generator, and `VerifyBlobFile`, which opens blob files, reads headers/records/footer with `BlobLogSequentialReader`, and validates blob indexes point to the correct file number and offset. `BuildAndCheckOneFile` writes multiple blobs into one file; `BuildAndCheckMultipleFiles` forces one blob per file; `InlinedValues` verifies below-threshold values create no files/additions. `Compression` validates Snappy-compressed records and metadata byte counts. `CompressionError` injects a compression corruption and checks path tracking without addition. `Checksum` uses a dummy checksum factory. Parameterized `BlobFileBuilderIOErrorTest` injects errors at file creation, header write, record write, and footer append.

## Dependencies, Risks, and Test Signals
The tests depend on mock env, blob log reader/writer, file naming, compression support, sync points, and checksum factories. They provide strong file-format and metadata signals but do not deeply test cache prepopulation or completion callback side effects.
