## sources/sync-backup/kopia/internal/blobparam/blobid_params.go

Purpose: structured logging parameter helpers for blob IDs and metadata.

Important APIs/types/functions: `BlobMetadataList`, `BlobID`, `BlobIDList`, `BlobMetadata`, and the corresponding `WriteValueTo` implementations.

Control flow, state, and persistence: each helper stores a field key and value/list; `WriteValueTo` emits JSON fields or lists through `contentlog.JSONWriter`. Metadata emits `blobID`, `l`, and `ts` fields.

Dependencies and integration points: integrates repository blob metadata with Kopia content logging infrastructure.

Risks and test signals: risks include field-name drift or inconsistent abbreviations (`l` for length). No direct tests in this subset; correctness depends on log consumers and JSON writer behavior.
