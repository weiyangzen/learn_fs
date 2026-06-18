# sources/sync-backup/kopia/repo/content/indexblob/index_blob_manager_v0_test.go

## Purpose
Tests the v0 index-blob manager under deterministic and randomized eventual-consistency scenarios. The tests validate the lifecycle of index blobs, compaction logs, cleanup records, and content deletion markers.

## Important APIs, Types, And Functions
Major tests are `TestIndexBlobManager`, `TestIndexBlobManagerStress`, `TestIndexBlobManagerPreventsResurrectOfDeletedContents`, `TestCompactionCreatesPreviousIndex`, and `TestIndexBlobManagerPreventsResurrectOfDeletedContents_RandomizedTimings`. Helpers create fake content-index entries, fake indexes, fake compactions, random writes/deletes/undeletes, active-index reads, and count checks for v0 blob prefixes. `newIndexBlobManagerForTesting` builds a `ManagerV0` with map storage, `ownwrites`, test crypto, and test hashing.

## Control Flow
The deterministic test writes several index blobs, registers compactions, advances fake storage time, and asserts the active blob list plus physical blob counts. The stress test starts multiple actors sharing storage; actors randomly read, write, delete, undelete, or compact, with only one actor allowed to compact. Resurrection tests generate sequences where deleted content and compaction overlap with visibility delays, then verify old contents do not reappear for either the writer or a separate reader.

## State And Persistence
All tests persist encrypted fake index JSON through `ManagerV0.WriteIndexBlobs` and compaction logs through `registerCompaction`. Separate fake local and storage clocks simulate clock drift and eventual consistency. `ownwrites.NewWrapper` models a client's read-your-own-writes behavior.

## Dependencies And Integration Points
The tests use `blobtesting`, `faketime`, `logging.NewWrapper`, `testlogging`, `ownwrites`, `blobcrypto.StaticCrypter`, `format.ContentFormat`, and encryption/hashing defaults. They exercise the same manager API used by production content code.

## Risks And Edge Cases
The most important tested risk is a compacted index with a deterministic blob ID causing a previously compacted input to be revived; fake indexes include a random ID to force unique output IDs. The stress test is intentionally nondeterministic and skipped/reduced in some environments. Several helpers retry when a listed blob disappears before read, matching eventual-consistency races.

## Test Signals
Strong behavioral coverage exists for v0 compaction ordering, delayed cleanup, concurrent actors, deleted-content dropping, and read-your-own-writes. It does not directly cover malformed compaction JSON or storage errors beyond missing blobs.
