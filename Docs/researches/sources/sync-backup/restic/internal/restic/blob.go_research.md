
# sources/sync-backup/restic/internal/restic/blob.go

Purpose: defines repository blob identity and blob metadata interfaces shared by repository, index, pack, prune, and repair code.

Important types are `PackBlob`, `BlobHandle`, `BlobType`, and `BlobHandles`. `PackBlob` intentionally exposes pack ID, handle, lengths, and compression status but not offset, keeping pack layout internal. `BlobHandle` pairs an `ID` with `BlobType`. `BlobType` enumerates invalid/data/tree blobs, provides strings, metadata classification, and JSON marshal/unmarshal. `BlobHandles` implements sorting by ID bytes then type and a string representation.

State is pure value data, serialized in indexes and JSON where blob types appear. Integration points are almost every repository layer: pack entries embed handles, indexes return `PackBlob`, prune operates on handles, and JSON tests enforce stable type names. Risks include adding blob types without updating JSON/string logic, treating tree blobs as metadata for backend/cache handling, and offset hiding requiring internal code to use `pack.Blob` when needed.
