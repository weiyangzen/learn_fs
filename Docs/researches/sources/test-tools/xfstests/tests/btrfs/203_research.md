# sources/test-tools/xfstests/tests/btrfs/203

## Purpose

`sources/test-tools/xfstests/tests/btrfs/203` is btrfs fstests case `203`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send operation works correctly when a file has shared extents with itself in the send snapshot, with a hole between them, and the file size has increased in the send snapshot. Create our test file with a size of 64K in the parent snapshot. After the parent snapshot is created, we will increase its size and then clone one of its extents into a different offset and leave a hole between the shared extents. The shared extents will be located at offsets greater then size of the file in the parent snapshot. Create a 320K extent at file offset 512K, with chunks of 64K having different content (to check cloning operations from send refer to the correct ranges).

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send clone` declares tags `auto quick send clone`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_test`, `_require_scratch_reflink`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch_reflink`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xf1 0 64K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/base`; `$BTRFS_UTIL_PROG send -f $send_files_dir/1.snap $SCRATCH_MNT/base 2>&1 \`; `$XFS_IO_PROG -c "pwrite -S 0xab 512K 64K" \`; `-c "pwrite -S 0xcd 576K 64K" \`; `$SCRATCH_MNT/incr 2>&1 | _filter_scratch`; `_md5_checksum $SCRATCH_MNT/incr/foobar`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send clone` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
