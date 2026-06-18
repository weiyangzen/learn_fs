<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_reader_test.cc

## Purpose
Tests `BlobFileReader` behavior across normal reads, multiget reads, format validation, compression, corruption, I/O failures, and file-size discovery. It provides regression coverage for low-level blob file reader contracts used by `BlobSource`, blob cache, and direct-write fallback.

## Important APIs, Types, and Functions
The test helper `WriteBlobFile` writes complete blob files with configurable column family, TTL flags, expiration ranges, compression, keys, values, offsets, and sizes. Filesystem wrappers simulate stale path sizes, open-handle `GetFileSize` failures, unsupported open-handle sizes, and fallback path-size failures. Test fixtures use `MockEnv`, `CompositeEnvWrapper`, `FaultInjectionTestEnv`, and sync points to inject read, decode, CRC, and decompression failures.

## Control Flow
Most tests create an isolated mock DB path, write a blob file through `BlobLogWriter`, create a `BlobFileReader`, then issue `GetBlob` and/or `MultiGetBlob` calls with chosen `ReadOptions`. Parameterized tests activate sync points at open, header read, footer read, blob read, or decode locations to verify errors surface at the right stage. Compression tests conditionally run when Snappy is available.

## State and Persistence Behavior
The test files are persisted in mock/fault-injection environments only. State under test includes encoded blob offsets/sizes, reader file-size selection, per-request status arrays, bytes-read counters returned by reads, and whether result buffers remain null on failure.

## Dependencies and Integration Points
The tests integrate blob log writer/format, reader, filename utilities, file options, writable-file writers, compression utilities, sync points, test harness, mock env, composite env, and fault-injection env. They indirectly validate agreements between writer offsets and reader offset validation.

## Risks and Edge Cases
The suite deliberately exercises offsets too close to file start/end, wrong compression, shorter or incorrect keys, incorrect value sizes, malformed files without footers, TTL or expiration ranges where non-TTL blob files are expected, wrong column family IDs, CRC mismatch, decompression corruption, I/O failures, and multiget requests where some entries fail validation before filesystem reads.

## Test Signals
Key named tests include `CreateReaderAndGetBlob`, file-size fallback/propagation tests, `Malformed`, `TTL`, `ExpirationRangeInHeader`, `ExpirationRangeInFooter`, `IncorrectColumnFamily`, `BlobCRCError`, `Compression`, `UncompressionError`, parameterized I/O and decoding error tests, and `MultiGetBlobWithFailedValidation`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_reader_test.cc -->
