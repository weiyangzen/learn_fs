# sources/object-store/rustfs/crates/e2e_test/src/copy_object_metadata_test.rs

## Purpose
This regression test verifies that self-copying an object with `MetadataDirective::Replace` updates metadata without losing or corrupting object data. It targets issue #2789.

## Important APIs, Types, and Functions
The test uses S3 `put_object`, `copy_object`, `head_object`, and `get_object`, with AWS SDK `MetadataDirective::Replace`. It relies on `RustFSTestEnvironment` for server lifecycle.

## Control Flow
The test uploads a JavaScript object with content type and two metadata keys, self-copies the object with replacement metadata that changes `mtime` and omits `stale`, verifies HEAD content length and metadata, verifies GET body equality, then self-copies again with empty replacement metadata and verifies omitted metadata stays absent while data remains readable.

## State and Persistence
State includes one bucket, one object, object body bytes, content type, and user metadata. CopyObject mutates metadata in place while preserving the underlying object payload.

## Dependencies and Integration Points
The test integrates CopyObject source handling, metadata replacement semantics, object metadata persistence, and read-after-copy data retrieval.

## Risks and Edge Cases
The test covers self-copy only, not cross-key or cross-bucket copies. It uses a small single-part object, so multipart copy behavior is not covered. It checks metadata removal and body preservation but not ETag/versioning interactions.

## Test Signals
Signals include content length equal to original length, updated `mtime`, removed `stale`, exact body after metadata replacement, absent metadata after empty replacement, and exact body after the second replacement.
