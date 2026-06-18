## sources/sync-backup/kopia/internal/blobtesting/asserts.go

Purpose: reusable assertions for blob storage provider tests.

Important APIs/types/functions: `AssertTimestampsCloseEnough`, `AssertGetBlob`, `AssertInvalidOffsetLength`, `AssertGetBlobNotFound`, `AssertInvalidCredentials`, `AssertGetMetadataNotFound`, `AssertListResults`, and `AssertListResultsIDs`.

Control flow, state, and persistence: helpers read blobs in full, zero-length, split-range, and invalid-range modes; verify not-found/credential errors; compare list and metadata results; and sort IDs for deterministic comparison. No persistence besides storage operations.

Dependencies and integration points: used by provider validation and in-memory storage tests. Depends on `gather.WriteBuffer`, `blob.Storage`, and test assertions.

Risks and test signals: timestamp tolerance is one minute to accommodate provider precision. `AssertGetBlob` assumes split reads are supported for blobs with length >=2. These helpers define expected storage contract behavior.
