
# sources/sync-backup/restic/internal/repository/repair_pack.go

Purpose: salvages intact blobs from specified pack files and then repairs indexes to drop broken pack references.

`RepairPacks` iterates requested pack IDs, loads pack entries from the index, attempts to copy all listed blobs through `CopyBlobs`, tracks successfully copied blobs, removes damaged pack files, and runs `RepairIndex` afterward to rebuild index state. It treats `io.ErrUnexpectedEOF` and corrupted blobs as salvageable failures where remaining valid blobs may still be copied; other errors are returned.

State changes include new replacement packs for successfully recovered blobs, deletion of specified bad pack files, and index rewrite through repair. Integration points are `CopyBlobs`, `LoadBlobsFromPack`, `RepairIndex`, progress counters, and backend pack removal. Risks include distinguishing expected corruption from fatal backend errors, avoiding deletion before recovery attempts, and ensuring already copied blobs are not lost if later blobs fail. Tests corrupt pack bytes and verify remaining blob sets after repair.
