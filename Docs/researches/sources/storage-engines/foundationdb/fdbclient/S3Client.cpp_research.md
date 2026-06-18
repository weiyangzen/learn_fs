# sources/storage-engines/foundationdb/fdbclient/S3Client.cpp

## Purpose
`S3Client.cpp` implements FoundationDB's asynchronous file/object transfer helpers for `blobstore://` S3-compatible backup URLs. It supplies the public helpers declared in `fdbclient/S3Client.h`: upload/download of files and directories, deletion, listing, bulk dump file-set upload, and local file checksum calculation. The implementation sits above `S3BlobStoreEndpoint`, `IAsyncFile`, Flow actors, and FoundationDB client knobs, so callers can use a single API for backup, bulk load/dump, CLI, and simulation workload paths without owning HTTP request details.

## Important APIs, types, and functions
`PartState` tracks one multipart transfer part: part number, file offset, size, ETag, per-part MD5 or SHA256 checksum, completion state, and uploaded bytes retained for ordered whole-object checksum calculation. `PartConfig` centralizes multipart size, retry delays, retry counts, retry cap, and checksum-validation enablement, mostly sourced from `CLIENT_KNOBS`.

`calculateFileChecksum()` streams an `IAsyncFile` in 64 KiB reads and returns a hex XXH64 digest. It validates short reads and frees the native xxhash state on both success and `Error` exceptions. `getEndpoint()` parses the `blobstore://` URL through `S3BlobStoreEndpoint::fromString`, applies the global proxy from `g_network`, validates that the `bucket` parameter exists, and restricts resource characters to alnum, `_`, `-`, `.`, and `/`.

Transfer helpers include `uploadPart()`, `copyUpFile(endpoint, bucket, object, filepath)`, public `copyUpFile(filepath, s3url)`, `copyUpDirectory()`, `copyUpBulkDumpFileSet()`, `downloadPart()`, `copyDownFile(endpoint, bucket, object, filepath)`, public `copyDownFile(s3url, filepath)`, `copyDownDirectory()`, `deleteResource()`, `listFiles()`, and `listFiles_impl()`. Checksum helpers prefer S3 object tags named `xxhash64` and fall back to a companion object with suffix `.checksum`.

## Control flow
Uploads parse a URL, open the local file uncached/no-AIO, start a multipart upload, and schedule `uploadPart()` actors in batches bounded by `BLOBSTORE_CONCURRENT_WRITES_PER_FILE`. Each part reads its byte range, computes SHA256/base64 when object integrity checking is enabled or MD5 otherwise, writes the part via `endpoint->uploadPart`, and retries retryable transport/storage errors with exponential delay. After all active futures complete, `copyUpFile()` finishes the multipart upload with the part ETags/checksums, then computes the whole-file XXH64 in part-number order from stored `partData`, writes the checksum tag or sidecar, and logs completion.

Downloads query object size, create the local parent directory, open an atomic read/write file, truncate it to the remote size, and schedule `downloadPart()` actors bounded by `BLOBSTORE_CONCURRENT_READS_PER_FILE`. Each part repeatedly calls ranged `readObject()` until its byte count is satisfied, optionally checks a per-part MD5 if populated, and writes to the local file offset. After all parts complete, the file is synced and the whole-file XXH64 is compared against the tag/sidecar checksum when present. Failure paths close/delete local files or abort multipart uploads where possible, then either retry file-level operations or rethrow.

Listing uses `S3BlobStoreEndpoint::listObjects()` for user-facing output and a lower-level `listFiles_impl()` that performs a list-type=2 GET and parses `ListBucketResult` XML through rapidxml.

## State and persistence behavior
The durable state touched here is outside FoundationDB key-value storage: S3 objects, S3 multipart upload sessions, optional object tags, optional checksum companion objects, and local files. `copyUpBulkDumpFileSet()` deletes an existing destination batch directory before uploading manifest/data/sample files. `copyDownFile()` writes through an atomic local file mode and deletes the partial file on terminal failure. No database transaction state is persisted by this file.

## Dependencies and integration points
The file depends on `S3BlobStoreEndpoint`, HTTP checksum helpers, `IAsyncFileSystem`, Flow actors/futures, `TraceEvent`, `CLIENT_KNOBS`, `platform::findFilesRecursively`, rapidxml, OpenSSL SHA256, libb64, and xxhash. It is used by the `s3client` CLI, bulk load/dump utilities, backup tests, `S3ClientWorkload`, and the `fdbclient/tests/s3client_test.sh` CTest targets. The public wrapper functions are the main integration surface.

## Risks and edge cases
`copyUpFile()` retains every uploaded part's data until after multipart completion so it can compute the ordered XXH64 digest; this avoids concurrent hash-state races but can scale memory usage up to the full file size. Empty remote objects are treated as `file_not_found()` on download because `objectSize <= 0` is rejected. The upload path appears to begin multipart upload even for a zero-length local file, leaving behavior dependent on endpoint handling of an empty ETag map. URL resource character validation is conservative and may reject object names that S3 itself accepts. Checksum validation is best effort for legacy objects: absence of tag and companion file logs `S3ClientNoChecksumFound` and allows download success. Retryable errors are explicitly enumerated, so new endpoint error codes may not retry until added.

## Test signals
Primary signals are `fdbclient/tests/s3client_test.sh`, `gcs_client_test`, bulkload tests that invoke `bin/s3client`, and simulation workloads `S3Client.toml` and `S3ClientWorkloadWithChaos.toml`. Useful assertions include multipart upload/download round trips, checksum tag and sidecar fallback, no-integrity-check knob behavior, listing depth/recursive output, nonexistent bucket/key errors, directory transfer path handling, and injected connection/HTTP failures.
