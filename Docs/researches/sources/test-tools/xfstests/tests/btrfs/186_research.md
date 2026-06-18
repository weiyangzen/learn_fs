# sources/test-tools/xfstests/tests/btrfs/186

## Purpose

`sources/test-tools/xfstests/tests/btrfs/186` is btrfs fstests case `186`. It targets send/receive stream correctness, multi-device or RAID volume behavior. Source comments describe the scenario as: Test that if we have a subvolume/snapshot that is writable, has a file with unflushed delalloc (buffered writes not yet flushed), turn the subvolume to readonly mode and then use it for send a operation, the send stream will contain the delalloc data - that is, no data loss happens. Create our test subvolume. Create our test file with some delalloc data. Turn our subvolume to RO so that it can be used for a send operation. Create the send stream. Recreate the filesystem and apply the send stream and verify no data was lost.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send volume` declares tags `auto quick send volume`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_test`, `_require_scratch`, `_require_btrfs_command "property"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `rm -fr $send_files_dir`; `_require_scratch`; `_require_btrfs_command "property"`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mkfs >>$seqres.full 2>&1`; `_scratch_mount`; `$BTRFS_UTIL_PROG subvolume create $SCRATCH_MNT/sv | _filter_scratch`; `$XFS_IO_PROG -f -c "pwrite -S 0xea 0 108K" $SCRATCH_MNT/sv/foo | _filter_xfs_io`; `$BTRFS_UTIL_PROG property set $SCRATCH_MNT/sv ro true`; `$BTRFS_UTIL_PROG send -f $send_files_dir/sv.send $SCRATCH_MNT/sv 2>&1 \`; `| _filter_scratch`; `od -t x1 -A d $SCRATCH_MNT/sv/foo`; `_scratch_unmount`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/sv.send $SCRATCH_MNT`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send volume` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
