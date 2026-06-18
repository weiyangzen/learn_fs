# sources/sync-backup/kopia/repo/blob/gcs/gcs_versioned.go

Purpose: provides GCS object-generation metadata helpers for point-in-time storage.

Important APIs/types/functions: `versionMetadata`, `versionMetadataCallback`, `getBlobVersions`, `listBlobVersions`, `list`, and `getVersionMetadata`.

Control flow: `getBlobVersions` lists versions for one exact blob prefix and returns `blob.ErrBlobNotFound` if none appear. `listBlobVersions` lists versions for all blobs with a prefix. The shared `list` function sets `storage.Query{Prefix, Versions:true}`, iterates object attrs, optionally stops when exact matching no longer applies, converts attrs to version metadata, and invokes callbacks. `getVersionMetadata` embeds normal blob metadata, marks delete state based on GCS `Deleted` time before the configured PIT, and stores generation as a decimal string.

State and persistence behavior: read-only interpretation of persisted GCS generations/deletion timestamps. No object mutation occurs.

Dependencies/integration points: used by `gcs_pit.go` and versioned integration tests. Risks include exact-match early return depending on iterator ordering, deletion semantics differing from providers with explicit delete markers, and generation parsing in `getBlobWithVersion`. Tests cover versioning disabled, multiple versions, and deletion scenarios.
