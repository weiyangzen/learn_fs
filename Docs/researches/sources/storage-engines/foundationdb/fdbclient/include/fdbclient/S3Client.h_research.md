# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/S3Client.h

## Purpose
`S3Client.h` declares high-level file and directory copy utilities built on `S3BlobStoreEndpoint`. It is the user-facing helper layer for copying local files/directories to and from S3-compatible blobstore URLs, listing resources, deleting resources, and computing file checksums.

## Important APIs, Types, And Functions
- `s3VerboseEventSev()` and `s3PerfEventSev()` choose trace severities based on simulation status and `S3CLIENT_VERBOSE_LEVEL`.
- `BLOBSTORE_PREFIX` is the expected URL prefix.
- `copyUpDirectory()`, `copyUpFile()`, `copyDownFile()`, and `copyDownDirectory()` move data between local filesystem and S3 resources.
- `copyUpBulkDumpFileSet()` uploads bulk dump file sets after clearing destination content.
- `deleteResource()` recursively deletes a blobstore file or directory.
- `calculateFileChecksum()` returns an xxhash64 checksum string for an async file.
- `listFiles()` lists S3 resources to a bounded depth.
- `getEndpoint()` parses URL resource and parameters and returns an S3 endpoint.

## Control Flow And State
Operations parse the blobstore URL, construct or obtain an endpoint, then perform object operations, often using multipart transfer for large files. Directory operations recurse, preserving path/resource mapping. Upload/download workflows include checksum calculation and verification, cleanup on failure, and parallel part transfer per the implementation.

## Persistence And External State
The header does not define stateful classes. External effects are local filesystem reads/writes and remote S3 object mutations. Checksum calculation reads local async file content.

## Dependencies And Integration Points
It depends on `S3BlobStore.h`, `BulkDumping.h`, Flow errors/network globals, and client knobs. It integrates backup, restore, bulk load/dump, and operational tools with S3-compatible storage.

## Risks And Edge Cases
Trace severity helpers dereference `g_network`, so callers need network setup. URL parsing must retain bucket/resource semantics consistently with `S3BlobStoreEndpoint`. Recursive delete/list/copy can be expensive or dangerous if resource prefixes are wrong. Checksum mismatches, partial local files, and failed multipart cleanup need careful handling in implementation.

## Test Signals
Tests should cover endpoint parsing, single-file upload/download, large multipart transfers, checksum mismatch behavior, recursive directory upload/download/delete, max-depth listing, bulk dump file set upload, simulated network severity levels, and cleanup after failures.
