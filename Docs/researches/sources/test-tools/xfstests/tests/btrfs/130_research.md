# sources/test-tools/xfstests/tests/btrfs/130

## Purpose

`sources/test-tools/xfstests/tests/btrfs/130` is btrfs fstests case `130`. It targets send/receive stream correctness. Source comments describe the scenario as: Check if btrfs send can handle large deduped file, whose file extents are all pointing to one extent. Such file structure will cause quite large pressure to any operation which iterates all backref of one extent. And unfortunately, btrfs send is one of these operations, and will cause softlock or OOM on systems with small memory(<4G). Use 128K blocksize, the default value of both deduperemove or inband dedupe create the initial file, whose file extents are all point to one extent create a RO snapshot, so we can send out the snapshot

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick clone send` declares tags `auto quick clone send`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_scratch`, `_require_scratch_reflink`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_scratch_reflink`; `_scratch_mkfs > /dev/null 2>&1`; `_scratch_mount`; `file=$SCRATCH_MNT/foobar`; `_pwrite_byte 0xcdcdcdcd 0 $blocksize  $file | _filter_xfs_io`; `_reflink_range $file 0 $file $(($i * $blocksize)) $blocksize \`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/ro_snap`; `echo "# $BTRFS_UTIL_PROG send $SCRATCH_MNT/ro_snap > /dev/null" >> $seqres.full`; `$BTRFS_UTIL_PROG send $SCRATCH_MNT/ro_snap > /dev/null 2>>$seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick clone send` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
