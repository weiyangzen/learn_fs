# sources/test-tools/xfstests/tests/btrfs/168

## Purpose

`sources/test-tools/xfstests/tests/btrfs/168` is btrfs fstests case `168`. It targets send/receive stream correctness. Source comments describe the scenario as: Test that we are able to do send operations when one of the source snapshots (or subvolume) has a file that is deleted while there is still a open file descriptor for that file. Create a subvolume used for first full send test and used to create two snapshots for the incremental send test. Create some test files. Flush the previous buffered writes, since setting a subvolume to RO mode does not do it and we want to check if the data is correctly transmitted by the send operations. Keep an open file descriptor on file bar.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send` declares tags `auto quick send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_btrfs_command "property"`, `_require_fssum`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch`; `_require_btrfs_command "property"`; `_require_fssum`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/sv1 | _filter_scratch`; `$XFS_IO_PROG -f -c "pwrite -S 0xf1 0 64K" $SCRATCH_MNT/sv1/foo >>$seqres.full`; `$XFS_IO_PROG -f -c "pwrite -S 0x7b 0 90K" $SCRATCH_MNT/sv1/bar >>$seqres.full`; `$FSSUM_PROG -r $send_files_dir/sv1.fssum $SCRATCH_MNT/sv1`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/snap1.send $SCRATCH_MNT`; `$FSSUM_PROG -r $send_files_dir/snap1.fssum $SCRATCH_MNT/snap1`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/snap2.send $SCRATCH_MNT`; `$FSSUM_PROG -r $send_files_dir/snap2.fssum $SCRATCH_MNT/snap2`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
