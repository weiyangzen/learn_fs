# sources/security-integrity/cryfs/crates/check/src/checks/parent_pointers.rs

Purpose: This check verifies that each reachable blob's stored parent pointer matches at least one parent blob that references it, and it also detects multiple references to the same blob.

Important APIs and flow: `CheckParentPointers` uses `ReferenceChecker<BlobId, SeenBlobInfo, BlobReference>`. The root blob is initially marked referenced as `BlobReference::root_dir()`. Readable blobs are marked seen with blob type and parent pointer; directory entries mark child blobs referenced with computed paths and entry types. Unreadable blobs are marked seen with the current reference. Finalization reports `BlobReferencedMultipleTimesError`, `WrongParentPointerError`, or adds assertions for unreadable/missing cases expected to be reported elsewhere.

State and persistence: The check builds an in-memory map of observed blob ids, observed parent pointers, and all incoming references. It does not write state and ignores unreachable nodes.

Dependencies and integration: It depends on `FsBlob`, `BlobType`, `EntryType`, `ReferenceChecker`, `BlobReference`, `MaybeBlobInfoAsSeenByLookingAtBlob`, and typed errors. It is called through `AllChecks` for every reachable blob.

Risks and test signals: `process_reachable_blob_again` is still TODO, so duplicate-reference behavior is currently handled mainly by the reference checker state accumulated from directory entries and first processing. Missing blobs are asserted through `NodeMissingError` because a blob's root node absence represents the missing blob at lower layers. It panics on impossible unreferenced reachable blobs.
