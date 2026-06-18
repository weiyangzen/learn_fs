# sources/test-tools/xfstests/tests/btrfs/189

## Purpose

`sources/test-tools/xfstests/tests/btrfs/189` is btrfs fstests case `189`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that an incremental send receive does not issue clone operations that attempt to clone the last block of a file, with a size not aligned to the filesystem's sector size, into the middle of some other file. Such clone request causes the receiver to fail (with EINVAL), for kernels that include commit ac765f83f1397646 ("Btrfs: fix data corruption due to cloning of eof block"), or cause silent data corruption for older kernels. Clone part of the extent from a higher offset to a lower offset of the same file. Now clone from the previous file, same range, into the middle of another file, such that the end offset at the destination is smaller than the destination's

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send clone` declares tags `auto quick send clone`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_fssum`, `_require_test`, `_require_scratch_reflink`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_fssum`; `_require_scratch_reflink`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xb1 0 2M" $SCRATCH_MNT/foo | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xc7 0 2M" $SCRATCH_MNT/bar | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0x4d 0 2M" $SCRATCH_MNT/baz | _filter_xfs_io`; `$XFS_IO_PROG -f -c "pwrite -S 0xe2 0 2M" $SCRATCH_MNT/zoo | _filter_xfs_io`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/1.snap $SCRATCH_MNT`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT`; `$FSSUM_PROG -r $send_files_dir/base.fssum $SCRATCH_MNT/base`; `$FSSUM_PROG -r $send_files_dir/incr.fssum $SCRATCH_MNT/incr`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send clone` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
