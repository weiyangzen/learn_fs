# sources/test-tools/xfstests/tests/btrfs/137

## Purpose

`sources/test-tools/xfstests/tests/btrfs/137` is btrfs fstests case `137`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that both incremental and full send operations preserve file holes. Create the first test file. Create a second test file with a 1Mb hole. Now add one new extent to our first test file, increasing its size and leaving a 1Mb hole between the first extent and this new extent. Now overwrite the last extent of our second test file. Create the send streams to apply later on a new filesystem. Create a new filesystem, receive the send streams and verify that the file contents are the same as in the original filesystem and that the file holes exists in both snapshots.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send fiemap` declares tags `auto quick send fiemap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/punch`; requirements: `_require_test`, `_require_scratch`, `_require_xfs_io_command "fiemap"`, `_require_btrfs_no_compress`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_btrfs_no_compress`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xaa -b 64k 0 64K" $SCRATCH_MNT/foo | _filter_xfs_io`; `-c "pwrite -S 0xaa -b 64k 0 64K" \`; `-c "pwrite -S 0xbb -b 64k 1088K 64K" \`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `$BTRFS_UTIL_PROG send -p $SCRATCH_MNT/snap1 -f $send_files_dir/2.snap \`; `$SCRATCH_MNT/snap2 2>&1 | _filter_scratch`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT >/dev/null`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT >/dev/null`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send fiemap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
