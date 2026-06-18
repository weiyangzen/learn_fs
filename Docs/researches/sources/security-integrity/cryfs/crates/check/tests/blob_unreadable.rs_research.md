## sources/security-integrity/cryfs/crates/check/tests/blob_unreadable.rs

Purpose: tests blob-level unreadability when individual nodes may still be readable, focusing on corrupt serialized blob metadata rather than missing/corrupted data-tree blocks.

Important APIs and functions: `unreadable_blob_bad_format_version` increments the blob format version via the fixture. `unreadable_file_blob_bad_blob_type` writes an invalid blob type byte. Both are parameterized over file, directory, symlink, and root directory blobs selected from `SomeBlobs`.

Control flow and state: each test creates a populated fixture, collects descendant blobs if the target is a directory, derives expected `NodeUnreferencedError`s for descendants that become unreachable when the directory cannot be decoded, mutates the raw blob header, runs `cryfs_check`, and asserts unordered equality against `BlobUnreadableError` plus descendant-root unreferenced errors.

Dependencies and integration: uses `BlobUnreadableError`, `CorruptedError`, `BlobReferenceWithId`, common `expect_blobs_to_have_unreferenced_root_nodes`, and fixture mutation methods. It integrates with fsblobstore deserialization semantics: bad format version or type makes the blob unreadable even when block integrity succeeds.

Risks and test signals: the tests confirm directory traversal cutoff behavior but do not inspect the precise low-level decode error. The final comment points to `blob_referenced_multiple_times` for unreadable blobs with duplicate references, avoiding duplicated coverage.
