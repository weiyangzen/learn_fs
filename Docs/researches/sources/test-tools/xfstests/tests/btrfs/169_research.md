# sources/test-tools/xfstests/tests/btrfs/169

## Purpose

`sources/test-tools/xfstests/tests/btrfs/169` is btrfs fstests case `169`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation produces correct results if a file that has a prealloc (unwritten) extent beyond its EOF gets a hole punched in a section of that prealloc extent. Create our test file with a prealloc extent of 4Mb starting at offset 0, then write 1Mb of data into offset 0. Now punch a hole starting at an offset that corresponds to the file's current size (1Mb) and ends at an offset smaller then the end offset of the prealloc extent we allocated earlier (3Mb < 4Mb). Now recreate the filesystem by receiving both send streams and verify we get the same file content that the original filesystem had.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send prealloc punch` declares tags `auto quick send prealloc punch`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_xfs_io_command "fpunch"`, `_require_xfs_io_command "falloc" "-k"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "falloc -k 0 4M" \`; `-c "pwrite -S 0xea 0 1M" \`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap1`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/snap1 2>&1 \`; `$SCRATCH_MNT/snap2 2>&1 | _filter_scratch`; `md5sum $SCRATCH_MNT/snap2/foobar | _filter_scratch`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send prealloc punch` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
