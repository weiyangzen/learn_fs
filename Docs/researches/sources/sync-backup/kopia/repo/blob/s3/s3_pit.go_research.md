# sources/sync-backup/kopia/repo/blob/s3/s3_pit.go

Purpose: implements point-in-time read-only views for S3-compatible versioned buckets.

Important APIs/types/functions: `s3PointInTimeStorage`, `ListBlobs`, `GetBlob`, `GetMetadata`, `getMetadata`, `newestAtUnlessDeleted`, `getOlderThan`, and `maybePointInTimeStore`.

Control flow: PIT listing requests object versions by prefix, groups versions by blob ID, and emits the newest version at or before the configured time unless it is a delete marker. PIT `GetBlob` and `GetMetadata` resolve version metadata through `getMetadata` and delegate to version-specific reads/metadata. `getOlderThan` filters version slices by timestamp; comments note S3 ordering differs from Azure/GCS. `maybePointInTimeStore` wraps only when a non-zero point-in-time is configured and returns a readonly wrapper after validating version access.

State and persistence behavior: the wrapper is read-only and interprets persisted S3 object versions/delete markers. No mutation occurs through the PIT view.

Dependencies/integration points: depends on S3 storage/versioned helpers defined in neighboring files, `readonly.NewWrapper`, and S3 versioning/list-object-versions semantics. Risks include provider-compatible services with non-AWS ordering or delete-marker behavior, timestamp precision around the PIT boundary, and versioning disabled/missing repository probes. Full tests for S3 PIT are outside the supplied file list, so this section relies on code-level inspection rather than local test signals.
