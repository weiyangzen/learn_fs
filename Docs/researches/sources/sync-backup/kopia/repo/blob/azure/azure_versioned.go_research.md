# sources/sync-backup/kopia/repo/blob/azure/azure_versioned.go

Purpose: defines Azure version metadata helpers used by point-in-time storage.

Important APIs/types/functions: `versionMetadata`, `versionMetadataCallback`, `getVersionedBlobMeta`, and `getBlobVersions`. `versionMetadata` embeds `blob.Metadata` and adds `Version` plus `IsDeleteMarker`.

Control flow: `getVersionedBlobMeta` requires `BlobItem.VersionID`, converts the Azure list item into normal blob metadata, and annotates delete-marker status via `isAzureDeleteMarker`. `getBlobVersions` delegates to `listBlobVersions`, tracks whether any versions were found, calls the callback for each, and returns `blob.ErrBlobNotFound` when nothing matched.

State and persistence behavior: no mutation; it interprets Azure's persistent version list and metadata into Kopia's PIT model. The `Version` string is expected to follow Azure's RFC3339Nano-like version ID semantics used elsewhere for delete-marker filtering.

Dependencies/integration points: used by `azure_pit.go` and tested by versioned integration tests. Risks include hard failure when versioning is disabled because `VersionID` is nil, and relying on Azure list item fields included by the caller. Tests cover disabled versioning and version/deletion scenarios.
