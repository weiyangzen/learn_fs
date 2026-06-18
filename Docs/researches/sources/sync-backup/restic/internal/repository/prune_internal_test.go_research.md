
# sources/sync-backup/restic/internal/repository/prune_internal_test.go

Purpose: tests a subtle prune accounting case involving duplicate used blobs.

`TestPruneMaxUnusedDuplicate` constructs packs containing distinct used blobs plus a duplicated blob across all packs. It forces one packer, writes large blobs to avoid small-pack repacking, and marks all blobs as used. The prune options allow some unused bytes but less than one blob. The test asserts the plan repacks duplicates correctly rather than treating all duplicated storage as tolerable unused space.

State is a real test repository with blob upload and index state. The test targets `packInfoFromIndex` and `decidePackAction` duplicate handling, especially the logic that keeps one occurrence of a duplicate and marks the rest removable. Risk covered: a prune plan could leave duplicate data behind or incorrectly remove all copies if duplicate counters and global size stats drift.
