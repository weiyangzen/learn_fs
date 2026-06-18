# sources/security-integrity/cryfs/crates/check/src/node_info/blob_info_as_seen_by_looking_at_blob.rs

Purpose: This enum describes what was observed when a blob was loaded directly.

Important APIs and flow: `BlobInfoAsSeenByLookingAtBlob` has `Unreadable` and `Readable { blob_type, parent_pointer }`. It derives equality, ordering, hashing, clone, copy, and debug traits.

State and persistence: It is value-only diagnostic state used while classifying blob observations and building errors.

Dependencies and integration: It depends on `BlobId` and fsblobstore `BlobType`. It converts into the `MaybeBlobInfoAsSeenByLookingAtBlob` superset in a sibling module.

Risks and test signals: It cannot represent missing blobs; callers use the `Maybe` wrapper when missing is possible.
