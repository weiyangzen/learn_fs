# sources/sync-backup/kopia/repo/blob/azure/azure_pit.go

Purpose: implements point-in-time read-only views for Azure Blob Storage using blob version listings.

Important APIs/types/functions: `azPointInTimeStorage`, `ListBlobs`, `GetBlob`, `newestAtUnlessDeleted`, `getOlderThan`, `listBlobVersions`, `getVersionedMetadata`, `isAzureDeleteMarker`, and `maybePointInTimeStore`.

Control flow: `maybePointInTimeStore` returns the raw storage when no point-in-time is configured; otherwise it probes repository blob versions to require versioning and wraps the PIT storage in `readonly.NewWrapper`. `ListBlobs` streams all versions by prefix, groups consecutive entries by blob ID, and emits the newest version not after the PIT unless that version is a delete marker. `GetBlob` resolves version metadata at the PIT and delegates to `getBlobWithVersion`.

State and persistence behavior: the wrapper does not mutate Azure state and exposes a historical view over persisted versions. Delete-marker treatment is provider-specific: Azure may report root blobs with `HasVersionsOnly`, and the code also handles Kopia's immutability workaround marker.

Dependencies/integration points: depends on Azure list include flags for metadata, deleted versions, and versions; uses `readonly` to prevent mutation; and uses `format.KopiaRepositoryBlobID` as a versioning sanity probe. Risks include assuming Azure version listing order, parsing delete-marker version IDs as RFC3339Nano, and returning nil on parse failure. Versioned tests cover ordering and deletion cases.
