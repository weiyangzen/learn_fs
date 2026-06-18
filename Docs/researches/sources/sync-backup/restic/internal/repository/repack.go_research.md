
# sources/sync-backup/restic/internal/repository/repack.go

Purpose: copies selected blobs out of selected packs into new packs, used by prune and repair workflows.

Important APIs are `CopyBlobs` and internal `repack`. The caller supplies source repository, destination repository/uploader, pack IDs, and a mutable `keepBlobs` set. `CopyBlobs` checks connection count for same-repository repacks, sets progress max, and delegates. `repack` optionally warms up cold-storage packs, lists target packs from the index, filters each pack's blob list against `keepBlobs`, and starts download workers. Each worker loads blobs from packs, rechecks/deletes the keep marker under a mutex so duplicates are saved once, and saves required blobs with `storeDuplicate=true`.

State changes are in destination packs and the caller's keep set; this function does not remove old packs or rewrite indexes directly. Integration points include `PrunePlan.Execute`, `RepairPacks`, repository warmup, `LoadBlobsFromPack`, and async blob uploading. Risks include concurrent duplicate handling, ensuring uploads can proceed by reserving one connection, context cancellation, cold-storage waits, and leaving unrepacked blobs detectable by a non-empty keep set. Tests in `repack_test.go` cover random selection, empty repacks, wrong blobs, and repair interactions.
