<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dirtree/dirtree_test.go -->
# sources/user-network-fs/rclone/fs/dirtree/dirtree_test.go

## Purpose
Unit and benchmark coverage for `DirTree`.

## Important APIs, Types, And Control Flow
Tests validate `New`, `parentDir`, `Add`, `AddDir`, `AddEntry`, `Find`, `checkParent`, `CheckParents`, `Sort`, `Dirs`, and `Prune` using string snapshots. The benchmark measures `CheckParents` over increasing flat directory counts.

## State And Persistence
Only in-memory mock entries and trees are used.

## Dependencies And Integration Points
Uses `fstest/mockdir` and `mockobject`, plus testify.

## Risks And Test Signals
Snapshot strings give strong structural coverage, though synthesized parent modtimes are not asserted. Benchmark highlights scalability risk in parent synthesis.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dirtree/dirtree_test.go -->
