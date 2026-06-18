# sources/security-integrity/cryfs/crates/check/src/node_info/maybe_blob_info_as_seen_by_looking_at_blob.rs

Purpose: This enum extends blob observation info with a `Missing` state for diagnostics where the blob could not be found.

Important APIs and flow: Variants are `Missing`, `Unreadable`, and `Readable { blob_type, parent_pointer }`. The `From<BlobInfoAsSeenByLookingAtBlob>` implementation maps unreadable/readable observations into the superset.

State and persistence: It is immutable error context, commonly used by blob multiple-reference diagnostics and display helpers.

Dependencies and integration: It depends on `BlobId`, `BlobType`, and `BlobInfoAsSeenByLookingAtBlob`.

Risks and test signals: The enum captures high-level load state but not root-cause errors or child lists. That keeps diagnostics compact but may omit repair clues.
