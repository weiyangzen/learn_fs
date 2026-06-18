
# sources/sync-backup/restic/internal/repository/repack_test.go

Purpose: integration-tests repacking and helper functions used by prune and repair tests.

Helpers create random blobs across pack files, split blob sets, list packs/indexes, find packs containing selected blobs, run `CopyBlobs`, remove old packs, and rebuild/reload indexes. `TestRepack` verifies empty repacks are no-ops, then repacks selected packs while keeping chosen blobs and checks repository consistency. Additional tests exercise wrong blob IDs, missing blobs, and combinations that ensure only requested blobs survive after index rebuild.

State is full repository state with pack files and indexes; tests intentionally mutate backend state by removing old packs after copy. Integration points include `CopyBlobs`, `RepairIndex`, `ListPackHandles`, `LookupBlob`, and checker validation. Risks covered include duplicate or missing blob handling, data preservation during pack replacement, index repair after manual pack removal, and cross-version behavior via `TestAllVersions`.
