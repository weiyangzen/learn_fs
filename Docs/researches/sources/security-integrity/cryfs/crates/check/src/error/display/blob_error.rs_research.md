# sources/security-integrity/cryfs/crates/check/src/error/display/blob_error.rs

Purpose: This module provides shared display formatting for blob-related corruption errors.

Important APIs and flow: `BlobErrorDisplayMessage` combines an `ErrorTitle` and `ErrorDisplayBlobInfo`. `display` writes the title, all references, blob id, and blob info. Helper functions render blob references and missing/unreadable/readable blob info including type and parent pointer.

State and persistence: It has no persistent state. It consumes iterator inputs over references and writes to a formatter.

Dependencies and integration: It depends on `console::style`, `BlobId`, `BlobType`, `BlobReference`, and `MaybeBlobInfoAsSeenByLookingAtBlob`. Blob error `Display` implementations compose this type.

Risks and test signals: The reference iterator is consumed exactly once, so callers pass iterators from deterministic sets. ANSI styling is stripped in tests for stable assertions; changes in text shape affect many display tests.
