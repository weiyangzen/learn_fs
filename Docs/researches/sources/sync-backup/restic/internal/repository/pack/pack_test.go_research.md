
# sources/sync-backup/restic/internal/repository/pack/pack_test.go

Purpose: tests exported pack creation, listing, backend-backed random reads, JSON blob type compatibility, writer failure behavior, and pack merging.

Key helpers are `createBuffers`, `newPack`, and `verifyBlobs`. `TestCreatePack` writes random blobs and verifies decoded header entries, lengths, offsets, and payload bytes. `TestUnpackReadSeeker` saves a pack to an in-memory backend and reads it through `backend.ReaderAt`. `TestShortPack` checks a single-blob pack. `TestPackerBroken` verifies the first write error is recorded and subsequent `Add`/`Finalize` return `ErrBroken`. `TestPackMerge` merges two packers and confirms all blobs remain readable.

Persistence behavior is represented by actual pack bytes and backend save/load. Risks covered include offset/header consistency, compressed-entry accounting, broken writer reuse, and merge reading from another packer's data stream. These tests give high confidence that pack files created by repository upload code are parseable by index repair and load paths.
