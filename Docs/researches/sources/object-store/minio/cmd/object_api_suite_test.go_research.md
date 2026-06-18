# sources/object-store/minio/cmd/object_api_suite_test.go

## Purpose
This file is a direct `ObjectLayer` behavioral suite. It bypasses HTTP routing and checks core bucket/object operations against the object-layer interface across FS/erasure-style harnesses and, for selected tests, compression/encryption/versioning combinations.

## Important APIs, Types, and Functions
- `newTestReaderEOF`, `newTestReaderNoEOF`, `testOneByteReadEOF`, and `testOneByteReadNoEOF` model readers that return data with or without EOF on the first read.
- Bucket/object tests include `testMakeBucket`, `testMultipleObjectCreation`, `testPutObject`, `testPutObjectInSubdir`, `testListBuckets`, `testListBucketsOrder`, `testPaging`, `testObjectOverwriteWorks`, and negative bucket/object cases.
- Multipart tests include `testMultipartObjectCreation` and `testMultipartObjectAbort`.
- `enableCompression`, `enableEncryption`, `resetCompressEncryption`, `execExtended`, and `ExecExtendedObjectLayerTest` manage global compression/encryption/KMS test modes.

## Control Flow
Each public `Test...` delegates to `ExecObjectLayerTest` or `ExecExtendedObjectLayerTest`, which supplies an `ObjectLayer`, instance label, and test error handler. Tests create buckets, write objects or multipart parts, call object-layer APIs, then verify returned errors, sizes, ETags, listing order, object data, and content-type inference. `execExtended` defines a matrix of default, versioned, compressed, compressed+versioned, encrypted, encrypted+versioned, compressed+encrypted, and compressed+encrypted+versioned runs.

## State and Persistence Behavior
The suite creates buckets, object keys, multipart upload IDs, part records, completed multipart objects, aborted uploads, overwritten objects, nested-prefix objects, and bucket lists. It verifies persistence by direct reads through `GetObject`, `GetObjectInfo`, and listing APIs. Compression/encryption helpers mutate package globals (`globalCompressConfig`, `globalAutoEncryption`, `GlobalKMS`) to force object metadata and storage behavior under different configurations.

## Dependencies and Integration Points
The tests exercise the `ObjectLayer` contract directly and therefore validate storage implementations independent of HTTP handlers. They use MinIO KMS secret-key parsing, humanize size constants, context timeouts, object options, bucket options, multipart structs, and shared put-reader helpers. HTTP handler tests rely on the same object-layer behavior for setup and verification.

## Risks and Edge Cases
- Global compression/encryption state must be reset or tests can contaminate each other.
- `ExecExtendedObjectLayerTest` currently accepts an `init` function in `execExtended` but calls `ExecObjectLayerTest` without visibly invoking that `init` in this file, so the effective matrix depends on harness behavior outside this file.
- Paging and ordering assertions encode lexicographic S3 listing behavior; implementation changes in ordering/token logic will break them.
- Tests compare exact error strings in several places, making error wording part of the contract.

## Test Signals
Signals include bucket creation and duplicate-bucket failure, multipart ETag formation and abort success, multiple object creation/readback, list pagination/truncation/prefix/delimiter/marker behavior, overwrite correctness, non-existent bucket/object errors, directory pseudo-object handling, content-type inference, bucket list order, and reader EOF edge cases.
