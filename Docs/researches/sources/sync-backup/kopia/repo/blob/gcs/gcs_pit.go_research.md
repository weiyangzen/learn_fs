# sources/sync-backup/kopia/repo/blob/gcs/gcs_pit.go

Purpose: implements read-only point-in-time views for versioned GCS buckets.

Important APIs/types/functions: `gcsPointInTimeStorage`, `ListBlobs`, `GetBlob`, `GetMetadata`, `getVersionedMetadata`, `newestAtUnlessDeleted`, `getOlderThan`, and `maybePointInTimeStore`.

Control flow: `maybePointInTimeStore` returns raw storage when no PIT is configured; otherwise it reads bucket attributes, requires versioning, and wraps a PIT storage in `readonly.NewWrapper`. PIT listing groups version metadata by blob ID and emits the newest version not after the PIT unless considered deleted. PIT reads resolve version metadata and pass the generation to `getBlobWithVersion`; metadata returns the resolved version metadata.

State and persistence behavior: no mutations are allowed through the PIT wrapper. Historical state comes from GCS object generations and deletion timestamps.

Dependencies/integration points: depends on `gcs_versioned.go`, GCS bucket versioning, and the readonly wrapper. Risks include assuming GCS version iteration order, interpreting deletion based on `Deleted` timestamp relative to PIT, and requiring bucket attribute permissions. Versioned tests cover disabled versioning, multiple versions, and deletion behavior.
