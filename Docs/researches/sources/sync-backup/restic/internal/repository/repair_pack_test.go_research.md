
# sources/sync-backup/restic/internal/repository/repair_pack_test.go

Purpose: tests pack salvage from broken pack files.

Helpers include `listBlobs`, which lists all indexed blobs, and `replaceFile`, which loads a backend file, mutates bytes, removes the original, and saves the damaged bytes back under the same handle. `TestRepairBrokenPack` delegates to versioned tests that create repositories, damage selected pack content, run `RepairPacks`, reload indexes, and compare blob sets before and after.

State is intentionally corrupted pack persistence in the backend. Integration points include pack loading, blob copy fallback, backend removal, repair index, and checker validation. Risks covered include failing to salvage intact blobs from partially damaged packs, leaving corrupted pack references in indexes, and version-specific differences in compressed/uncompressed pack contents.
