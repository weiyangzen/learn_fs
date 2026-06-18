<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/test_util.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/test_util.go

## Purpose
This file contains shared helper functions for downloader testify and parallel tests. It reduces duplication around retrieving fake object metadata, validating local cache file contents, and validating file-info cache entries.

## Important APIs
`getMinObject` stats an object from a test bucket with `ForceFetchFromGcs` and returns a value. `verifyFileTillOffset` checks file existence, permissions, and content prefix up to a requested offset. `verifyCompleteFile` checks permissions, size, and full content. `verifyFileInfoEntry` retrieves cache metadata and asserts generation, downloaded offset, and content size. `getFileInfo` builds a `data.FileInfoKey` and looks it up in the LRU cache.

## Control flow and state behavior
The helpers are assertion wrappers rather than production logic. They encode important expectations: cache files use the configured `FileSpec.FilePerm`; parallel downloads may leave file size larger than object content until final truncation, so complete validation accepts file size greater than or equal to content length; and file-info offsets are allowed to be greater than or equal to the expected offset.

## Dependencies and integration points
The file depends on `testing`, `testify/assert`, `os`, `reflect`, `data.FileSpec`, `lru.Cache`, fake/mock storage bucket types, and GCS object metadata. It is used by testify suites and manager parallel tests to validate downloader side effects consistently.

## Risks and edge cases
`getMinObject` panics on stat errors, which is acceptable for test setup but hides test helper failure as panic rather than assertion. Content comparison reads the whole file into memory, which is fine for current test sizes but would be expensive for very large fixtures. The prefix validators rely on the caller passing an offset no larger than the expected content length.

## Test signals
Although it has no tests of its own, this file centralizes the signal that downloader tests care about three persistent side effects: local cache file permissions/content, file-info cache generation/offset/content-size, and object metadata retrieval from fake storage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/test_util.go -->
