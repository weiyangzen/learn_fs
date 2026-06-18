# sources/test-tools/syzkaller/pkg/asset/backend_dummy.go

## Purpose
In-memory/dummy asset storage backend for debugging and tests.

## Important APIs, Types, and Functions
`dummyStorageBackend` tracks current time, object metadata, and optional upload/remove callbacks. Methods implement `StorageBackend`: `upload`, `downloadURL`, `getPath`, `list`, `remove`, plus test helper `hasOnly`. `dummyWriteCloser` discards bytes.

## Control Flow
Uploads record object metadata and delegate to callback or return a discard writer. URLs are mapped to/from `http://download/` paths, with a special unknown-bucket URL. Listing converts map entries to `gcs.Object`; removal invokes callback, checks existence, and deletes.

## State and Persistence Behavior
State is an in-memory map of path to creation/content metadata. It is lost when the backend is dropped.

## Dependencies and Integration Points
Used by `StorageFromConfig` for `dummy://` and by storage tests to inspect uploads/deletions.

## Risks and Test Signals
Not concurrency-safe and does not store bytes unless callbacks do. Tests use it to validate compression, deprecation, duplicate handling, and URL parsing paths.
