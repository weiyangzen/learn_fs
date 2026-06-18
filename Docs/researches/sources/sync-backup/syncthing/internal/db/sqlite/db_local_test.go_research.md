# sources/sync-backup/syncthing/internal/db/sqlite/db_local_test.go

## Purpose
This test file validates local file, blocklist, block index, and remote sequence behavior in the SQLite backend.

## Important APIs and Control Flow
`TestBlocks` checks block-hash lookup for local files. `TestBlocksDeleted` verifies that replacing a local file's blocks removes old block hits through file-row replacement and deferred block filtering. `TestDropBlockIndex`, `TestPopulateBlockIndex`, and `TestPopulateBlockIndexSkipsRemoteFiles` exercise optional block index maintenance. `TestSkipBlockIndexOnUpdate` proves file blocklists remain retrievable even when `db.WithSkipBlockIndex` avoids populating `blocks`. `TestRemoteSequence` asserts `RemoteSequences` tracks highest remote sequence per device.

## State and Persistence Behavior
The tests distinguish `blocklists` storage from `blocks` index rows. FileInfo retrieval reconstructs blocks from stored blocklists, while `AllLocalBlocksWithHash` uses the `blocks` table filtered through live local `files` rows. Remote files may store blocklists but are not inserted into the local block index.

## Dependencies and Integration Points
The tests use public `DB` methods, `itererr.Collect`, `protocol.DeviceID`, `protocol.LocalDeviceID`, and helper file/block generators from `db_test.go`. They directly exercise `folderdb_update.go` block insertion and `folderdb_local.go` block queries.

## Risks and Test Signals
Important risks are stale block hits after file replacement, rebuilding the block index from blocklists, and preserving file retrieval when indexing is skipped. The tests also confirm no-op behavior when dropping an empty or nonexistent block index.
