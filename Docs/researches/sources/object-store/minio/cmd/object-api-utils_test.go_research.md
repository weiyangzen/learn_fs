# sources/object-store/minio/cmd/object-api-utils_test.go

## Purpose
This file tests and benchmarks the object API utility layer. It validates path joining and concatenation performance, object and bucket validation, Windows path traversal protection, multipart ETag generation, metadata cleanup, compression metadata semantics, compression policy, compressed range offset math, S2 compression reader behavior, and path cleaning detection.

## Important APIs, types, and functions
- `pathJoinOld` and `concatNaive` are baseline implementations used by benchmarks.
- `BenchmarkConcatImplementation`, `BenchmarkPathJoinOld`, and `BenchmarkPathJoin` measure optimized helpers.
- `TestPathTraversalExploit` runs only on Windows and drives a signed HTTP PUT through the API router.
- `TestIsValidBucketName`, `TestIsValidObjectName`, and `TestIsMinioMetaBucketName` cover validation rules.
- `TestGetCompleteMultipartMD5`, `TestRemoveStandardStorageClass`, `TestCleanMetadata`, and `TestCleanMetadataKeys` cover metadata helpers.
- `TestIsCompressed`, `TestExcludeForCompression`, `TestGetActualSize`, `TestGetCompressedOffsets`, `TestS2CompressReader`, and `Test_pathNeedsClean` cover compression-related behavior.

## Control flow
The Windows path traversal regression initializes test config, sends a signed PUT for an object name containing a backslash traversal into `.minio.sys`, then directly inspects erasure disks with `readAllFileInfo` to ensure no backend part was written with that unsafe name. Validation tests use explicit tables of accepted and rejected bucket/object names, including IP-like buckets, uppercase names, dot/dash boundary cases, UTF-8 names, relative-path attempts, double slashes, invalid bytes, and trailing slash object names.

Compression tests construct `ObjectInfo` values with reserved metadata and parts. They confirm known compression algorithms are accepted, unknown algorithms return an error while still indicating compressed metadata is present, actual size can come from metadata or part sums, and missing actual-size evidence is invalid. `TestS2CompressReader` streams empty, small, and large payloads through `newS2CompressReader`, compares output with a standard S2 writer, verifies large-stream indexes, and round-trips decompression.

## State and persistence behavior
Most tests are pure unit tests over in-memory maps, headers, and readers. `TestPathTraversalExploit` is integration-like: it writes through the HTTP stack to a real test erasure object layer and inspects on-disk object metadata. The benchmark tests do not persist state. Compression reader tests exercise goroutine and pipe behavior by fully reading and closing the returned reader before consuming the index callback.

## Dependencies and integration points
The tests use MinIO's object-layer API test harness, auth credentials, signed request helpers, S2 compression package, compression config, crypto metadata keys, trie utilities, and standard `httptest`. They are directly tied to utility functions from `object-api-utils.go` and indirectly to handler/router behavior for the path traversal regression.

## Risks and edge cases
The Windows-only traversal test can silently skip on non-Windows builders, so cross-platform CI must include Windows to retain that signal. Validation tables encode MinIO-specific differences from S3, such as rejecting trailing slash object names in `IsValidObjectName` while lower object-layer tests still allow certain empty directory marker writes. `TestGetActualSize` ignores returned errors in assertions, so it primarily validates sentinel sizes rather than exact error classes.

## Test signals
This file provides strong regression coverage for security-sensitive path handling, metadata normalization, and compression helper behavior. It is less exhaustive for encrypted compressed ranges with populated S2 indexes, direct `NewGetObjectReader` closure behavior, and disk-space checks.
