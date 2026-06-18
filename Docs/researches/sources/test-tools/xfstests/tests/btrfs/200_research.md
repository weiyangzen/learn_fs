# sources/test-tools/xfstests/tests/btrfs/200

## Purpose

`sources/test-tools/xfstests/tests/btrfs/200` is btrfs fstests case `200`. It targets send/receive stream correctness. Source comments describe the scenario as: Check that send operations (full and incremental) are able to issue clone operations for extents that are shared between the same file. Create our first test file, which has an extent that is shared only with itself and no other files. We want to verify a full send operation will clone the extent. Create out second test file which initially, for the first send operation, only has a single extent that is not shared. Now clone the existing extent in file bar to itself at a different offset. We want to verify the incremental send operation below will issue a clone operation instead of a write operation.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send clone fiemap` declares tags `auto quick send clone fiemap`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`; snapshot equivalence is checked with `$FSSUM_PROG`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`, `./common/punch`; requirements: `_require_fssum`, `_require_test`, `_require_scratch_reflink`, `_require_xfs_io_command "fiemap"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_fssum`; `_require_scratch_reflink`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite -S 0xb1 -b 128K 0 128K" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foo 0 128K 128K" $SCRATCH_MNT/foo \`; `$XFS_IO_PROG -f -c "pwrite -S 0xc7 -b 128K 0 128K" $SCRATCH_MNT/bar \`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/base`; `$XFS_IO_PROG -r -c "fiemap" $SCRATCH_MNT/incr/foo`; `num_extents=$(_count_extents $SCRATCH_MNT/incr/bar)`; `num_exclusive_extents=$(_count_exclusive_extents $SCRATCH_MNT/incr/bar)`; `echo "File bar does not have 2 shared extents in the incr snapshot"`; `$XFS_IO_PROG -r -c "fiemap" $SCRATCH_MNT/incr/bar`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send clone fiemap` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. `fssum` manifests are written on source snapshots and verified after receive.
