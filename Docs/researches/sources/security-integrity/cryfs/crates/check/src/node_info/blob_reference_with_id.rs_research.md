# sources/security-integrity/cryfs/crates/check/src/node_info/blob_reference_with_id.rs

Purpose: This struct combines a concrete `BlobId` with the path/type/parent context represented by `BlobReference`.

Important APIs and flow: `BlobReferenceWithId` contains `blob_id` and `referenced_as`. Its `Display` renders type, path, blob id, and parent blob id; `Debug` wraps that display text.

State and persistence: It is diagnostic/reference state passed through the runner for reachable blobs and used in errors.

Dependencies and integration: It depends on `BlobId`, `BlobType`, and `BlobReference`. It appears in node references, root-node diagnostics, and conversion into `MaybeBlobReferenceWithId`.

Risks and test signals: Unit tests cover file, dir, and symlink display with ANSI stripping. Formatting is compact and used in debug messages such as runner logs.
