# sources/security-integrity/cryfs/crates/check/src/error/blob_unreadable.rs

Purpose: This file defines the corruption error for reachable blobs that fail to load.

Important APIs and flow: `BlobUnreadableError` stores `blob_id` and all known `referenced_as` `BlobReference`s. `new` constructs the error, and `Display` renders a blob error message with `MaybeBlobInfoAsSeenByLookingAtBlob::Unreadable`.

State and persistence: Diagnostic state is immutable and uses `BTreeSet` for deterministic output. The underlying load error is not stored yet; a TODO reserves space for an `anyhow::Error`.

Dependencies and integration: It is emitted by `CheckBlobsReadable` and asserted by parent-pointer and runner paths when unreadable blobs are observed.

Risks and test signals: Tests cover file, dir, symlink, and multi-reference display. Missing root-cause error details may limit repair diagnostics because the exact blockstore/blobstore read failure is discarded.
