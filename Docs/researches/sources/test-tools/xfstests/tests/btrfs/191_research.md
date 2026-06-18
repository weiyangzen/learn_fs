# sources/test-tools/xfstests/tests/btrfs/191

## Purpose

`sources/test-tools/xfstests/tests/btrfs/191` is btrfs fstests case `191`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works after deduplicating into the same file in both the parent and send snapshots. Create our first file. The first half of the file has several 64Kb extents while the second half as a single 512Kb extent. Create the base snapshot and the parent send stream from it. Create our second file, that has exactly the same data as the first file. Create the second snapshot, used for the incremental send, before doing the file deduplication. Now before creating the incremental send stream: 1) Deduplicate into a subrange of file foo in snapshot mysnap1. This will drop

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send dedupe` declares tags `auto quick send dedupe`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_test`, `_require_scratch_dedupe`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch_dedupe`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -s -c "pwrite -S 0xb8 -b 64K 0 512K" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "pwrite -S 0xb8 512K 512K" $SCRATCH_MNT/foo | _filter_xfs_io`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/mysnap1`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/mysnap1 2>&1 \`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$FSSUM_PROG -r $send_files_dir/1.fssum $SCRATCH_MNT/mysnap1`; `$FSSUM_PROG -r $send_files_dir/2.fssum $SCRATCH_MNT/mysnap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send dedupe` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
