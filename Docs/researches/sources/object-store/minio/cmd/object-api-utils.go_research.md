# sources/object-store/minio/cmd/object-api-utils.go

## Purpose
This file contains shared object API utilities used by MinIO handlers and object-layer code. It covers bucket and object name validation, path joining optimized for object paths, metadata cleanup, multipart ETag synthesis, compression eligibility and S2 compression helpers, object size interpretation for compressed/encrypted data, range translation, GET reader construction, PUT reader wrapping, and disk-space checks.

## Important APIs, types, and functions
- Constants define internal buckets and prefixes such as `.minio.sys`, multipart metadata, temporary metadata, compression thresholds, and compression padding.
- `IsValidBucketName`, `IsValidObjectName`, `IsValidObjectPrefix`, and `checkObjectNameForLengthAndSlash` enforce S3-compatible and filesystem-safe names, with Windows-specific invalid character handling.
- `pathJoin`, `pathJoinBuf`, `pathNeedsClean`, `retainSlash`, and `pathsJoinPrefix` provide low-allocation path operations while preserving significant trailing slashes.
- `getCompleteMultipartMD5`, `cleanMetadata`, `removeStandardStorageClass`, `cleanMetadataKeys`, and `extractETag` normalize metadata and S3 multipart ETag behavior.
- `ObjectInfo.IsCompressed`, `IsCompressedOK`, and `GetActualSize` interpret persisted metadata and part metadata for compressed and encrypted objects.
- `excludeForCompression`, `isCompressible`, `hasStringSuffixInSlice`, and `hasPattern` implement the compression policy.
- `getPartFile`, `partNumberToRangeSpec`, and `getCompressedOffsets` map logical parts/ranges to on-disk part files and compressed offsets.
- `GetObjectReader`, `NewGetObjectReaderFromReader`, and `NewGetObjectReader` wrap object readers with precondition, decryption, decompression, range, and cleanup semantics.
- `PutObjReader`, `NewPutObjReader`, `WithEncryption`, `MD5CurrentHexString`, and `RawServerSideChecksumResult` preserve original checksums while allowing encrypted writes.
- `newS2CompressReader` streams S2 compression through a pipe and optionally returns a seek index; `compressSelfTest` validates compression/decompression at startup.
- `getDiskInfos` and `hasSpaceFor` aggregate disk capacity and enforce write-space constraints.

## Control flow
Validation helpers reject dangerous path components, invalid UTF-8, double slashes, null bytes, overlong object names, and Windows-only forbidden characters. `pathJoinBuf` writes path segments into a pooled byte buffer, checks whether `path.Clean` is needed, and preserves the last argument's trailing slash when required.

`NewGetObjectReader` first evaluates any precondition callback, derives a range from a part number if necessary, detects encryption and compression metadata, and then returns a closure plus storage offset and length. For compressed objects it may translate decompressed ranges into compressed storage offsets with `getCompressedOffsets`, decrypt compressed indices when needed, attach a block decrypter, S2 reader, skip/limit logic, and optional readahead. For encrypted-only objects it computes encrypted read ranges and wraps the input reader in DARE decryption before limiting to the logical range. For plain objects it returns the original reader.

`newS2CompressReader` creates an `io.Pipe`, copies the input into an S2 writer in a goroutine, validates the expected original byte count, emits a stripped S2 index for large streams, and propagates copy/close errors through the pipe. `PutObjReader` keeps both the current write reader and raw original reader so ETags and server-side checksum results can be reported for plaintext input even after encryption wrappers are installed.

## State and persistence behavior
Most utilities are stateless, but several encode persistent metadata contracts: compression metadata uses reserved keys for algorithm and actual size; encrypted/compressed metadata may include encrypted compression indexes; storage class `STANDARD` is removed from response metadata; multipart ETags concatenate part MD5s and append the part count. `hasSpaceFor` reads `DiskInfo` from storage APIs and applies cluster-level availability, inode, per-disk free-space, and fill-fraction checks before writes proceed.

## Dependencies and integration points
This file integrates with MinIO object metadata (`ObjectInfo`, `ObjectPartInfo`, `ObjectOptions`), encryption helpers (`crypto`, DARE decryption, metadata encryption), hash readers, HTTP range parsing, compression config, DNS SRV discovery, byte buffer pooling, trie-based part lookup, wildcard MIME matching, readahead, and storage APIs. Handler code in `object-handlers.go` relies on these utilities for PUT/COPY reader setup, GET/HEAD range serving, compression, encryption, and checksum reporting.

## Risks and edge cases
Compression plus encryption range math is sensitive: wrong index decryption, padding, sequence number, or skip calculations can corrupt ranged reads. `concat` uses `unsafe.String` from a byte slice, so future changes must preserve the allocation lifetime assumptions. `newS2CompressReader` runs a goroutine and pipe; callers must close the reader on incomplete streams to avoid resource leaks. `pathNeedsClean` intentionally allows false positives but should not produce false negatives for paths that need cleaning. Disk-space checks are approximate and assume erasure overhead by multiplying size by two.

## Test signals
The paired utility tests cover bucket/object validation, path traversal regression, metadata cleaning, multipart MD5s, compression detection and policy, actual-size derivation, compressed offset mapping, S2 compression/index generation, and path-clean detection. The more complex `NewGetObjectReader` encryption/decompression combinations are indirectly covered through object handler and integration tests rather than direct exhaustive unit tests here.
