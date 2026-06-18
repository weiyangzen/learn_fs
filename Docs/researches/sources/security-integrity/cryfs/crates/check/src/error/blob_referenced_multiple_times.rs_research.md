# sources/security-integrity/cryfs/crates/check/src/error/blob_referenced_multiple_times.rs

Purpose: This file defines the corruption error for a blob id referenced by multiple parent directory entries.

Important APIs and flow: `BlobReferencedMultipleTimesError` contains `blob_id`, `blob_info: MaybeBlobInfoAsSeenByLookingAtBlob`, and `referenced_as: BTreeSet<BlobReference>`. `new` asserts at least two references. `Display` builds a shared `BlobErrorDisplayMessage` with title `BlobReferencedMultipleTimes`.

State and persistence: It is immutable diagnostic data. `BTreeSet` gives deterministic reference ordering for equality and display output.

Dependencies and integration: It is produced by `CheckParentPointers`, included in `CorruptedError`, and displayed through `error/display/blob_error.rs`.

Risks and test signals: Unit tests cover missing, unreadable, file/dir/symlink readable blobs, and many-reference formatting using `strip_ansi_codes`. The constructor invariant protects against malformed single-reference errors.
