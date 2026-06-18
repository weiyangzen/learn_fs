# sources/security-integrity/cryfs/crates/check/src/node_info/maybe_blob_reference_with_id.rs

Purpose: This enum records whether a node's owning blob is reachable from the filesystem root.

Important APIs and flow: Variants are `UnreachableFromFilesystemRoot` and `ReachableFromFilesystemRoot { blob_id, referenced_as }`. It implements `From<BlobReferenceWithId>` for reachable context.

State and persistence: It is reference context for node errors, especially orphaned or dangling subtrees discovered outside the root traversal.

Dependencies and integration: It depends on `BlobId`, `BlobReferenceWithId`, and `BlobReference`. `NodeAndBlobReference` uses it for non-root nodes.

Risks and test signals: Unreachable context intentionally lacks a blob id/path, so diagnostics for orphaned child nodes can be less specific than reachable nodes.
