# sources/storage-engines/rocksdb/db/db_follower_test.cc

## Purpose

`db_follower_test.cc` tests RocksDB's Linux-only follower mode, where a read-only follower DB catches up from a leader DB by reading the leader's MANIFEST and linking/copying needed table files into a follower directory. The suite focuses on catch-up races around flushes, compactions, MANIFEST rollover, intermediate obsolete files, and partial version recovery.

## Important APIs, Types, and Helpers

- `DBFollowerTest` derives from `DBTestBase`, creates separate leader and follower directories, and opens the leader under `dbname_/leader`.
- `OpenAsFollower()` calls `DB::OpenAsFollower(opts, follower_name_, dbname_, &follower_)` with a wrapped follower env and `follower_refresh_catchup_period_ms=100`.
- `FollowerGet()` reads with checksum verification and normalizes not-found/error statuses to strings for assertions.
- `CheckDirs()` compares table file numbers in leader and follower directories to ensure the follower has all needed SSTs.
- `DBFollowerTestFS` wraps descriptor-file sequential reads and provides barriers so tests can pause follower MANIFEST reads at controlled points.
- `DBFollowerTestSstPartitionerFactory` creates small partitioned SST outputs so partial recovery scenarios can produce multiple overlapping compaction files.

## Control Flow

`Basic` writes and flushes two keys before opening the follower, then verifies reads and directory parity. `Flush` uses sync points so the follower starts catch-up, the leader flushes a key, and the follower waits until catch-up finishes before reading it.

`RetryCatchup` creates four L0 files and compacts them while the follower is catching up. The follower can fail to instantiate versions for now-obsolete flushed files, then recover a valid version from the later compaction edit. `RetryCatchupManifestRollover` adds a leader reopen/MANIFEST rollover between flushes and compaction, requiring another refresh round because the follower does not switch manifests mid-read.

`IntermediateObsoleteFiles` uses filesystem read barriers so the follower first links four L0 files and then sees a compaction edit deleting them. It verifies those intermediate follower files are explicitly deleted and the final value remains readable.

`PartialVersionRecovery` and `PartialVersionRecoveryWithRollover` use an SST partitioner and small compaction bytes to generate overlapping compaction outputs. They verify that when some additions cannot be found or are added and deleted before catch-up installs a version, the follower still deletes obsolete files and eventually reads the correct point-in-time values. The rollover variant requires a second catch-up attempt after leader reopen.

## State and Persistence Behavior

The suite observes leader MANIFEST edits, leader table files, follower-linked table files, follower version installation, obsolete-file deletion, and persisted state after leader reopen. It deliberately creates table files that are transient in the leader but visible to the follower during catch-up. Correctness means the follower neither misses required live files nor keeps obsolete intermediate files after applying later version edits.

## Dependencies and Integration Points

The tests depend on `DB::OpenAsFollower`, follower refresh internals (`DBImplFollower::TryCatchupWithLeader` sync points), `VersionEditHandlerPointInTime`, background compaction purge points, filesystem wrappers, table-file naming helpers, checksum verification reads, manual compaction helpers, and Linux-specific file-linking behavior.

## Risks and Edge Cases

Follower catch-up is race-prone because the leader can flush, compact, purge obsolete files, and roll over the MANIFEST while the follower is reading. A follower can see edit records for files that have already disappeared, or it can link files that are later deleted by a subsequent compaction edit. MANIFEST rollover is especially subtle because a catch-up pass may end without installing a new version and must rely on the next refresh.

## Test Signals

Signals include follower point reads, checksum-verified `Get`, directory table-file-number parity, sync-point ordered catch-up completion, and successful cleanup of intermediate obsolete files. The file is compiled only under `OS_LINUX`, so cross-platform test coverage must come from other follower-mode tests or mocked behavior.
