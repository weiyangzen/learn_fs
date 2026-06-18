# sources/test-tools/xfstests/tests/btrfs/149

## Purpose

`sources/test-tools/xfstests/tests/btrfs/149` is btrfs fstests case `149`. It targets send/receive stream correctness, compression interactions. Source comments describe the scenario as: Test that an incremental send/receive operation will not fail when the destination filesystem has compression enabled and the source filesystem has an extent at a file offset 0 that is not compressed and that is shared. On 64K pagesize systems the compression is more efficient, so max_inline helps to create regular (non inline) extent irrespective of the final write size. Write to our file using direct IO, so that this way the write ends up not getting compressed, that is, we get a regular extent which is neither inlined nor compressed.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick send compress` declares tags `auto quick send compress`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_test`, `_require_scratch`, `_require_scratch_reflink`, `_require_odirect`, `_require_btrfs_command inspect-internal dump-super`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -fr $send_files_dir`; `rm -f $tmp.*`; `_require_scratch`; `_require_scratch_reflink`; `_require_btrfs_command inspect-internal dump-super`; `send_files_dir=$TEST_DIR/btrfs-test-$seq`; `mkdir $send_files_dir`; `_scratch_mount "-o compress -o max_inline=0"`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xab 0 $sectorsize" $SCRATCH_MNT/foobar |\`; `$BTRFS_UTIL_PROG subvolume snapshot -r $SCRATCH_MNT \`; `"reflink $SCRATCH_MNT/foobar 0 $((2 * $sectorsize)) $sectorsize" \`; `$BTRFS_UTIL_PROG receive -f $send_files_dir/2.snap $SCRATCH_MNT > /dev/null`; `sum_dest_snap1=$(md5sum $SCRATCH_MNT/mysnap1/foobar | $AWK_PROG '{print $1}')`; `sum_dest_snap2=$(md5sum $SCRATCH_MNT/mysnap2/foobar | $AWK_PROG '{print $1}')`; `[[ $sum_src_snap1 == $sum_dest_snap1 ]] && echo "src and dest 'mysnap1' checksum matched"`; `[[ $sum_src_snap2 == $sum_dest_snap2 ]] && echo "src and dest 'mysnap2' checksum matched"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Send streams, fssum manifests, and received snapshots are temporary artifacts used to compare source and reconstructed filesystems. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick send compress` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Send tests can be fragile around inode-number ordering, rename dependencies, clone commands, xattrs, and receiver mount options. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
