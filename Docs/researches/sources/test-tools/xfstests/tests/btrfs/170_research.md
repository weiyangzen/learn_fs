# sources/test-tools/xfstests/tests/btrfs/170

## Purpose

`sources/test-tools/xfstests/tests/btrfs/170` is btrfs fstests case `170`. It targets subvolume/snapshot metadata. Source comments describe the scenario as: Test that if we write into an unwritten extent of a file when there is no more space left to allocate in the filesystem and then snapshot the file's subvolume, after a clean shutdown the data was not lost. Use a fixed size filesystem so that we can precisely fill the data block group mkfs.btrfs creates and allocate all unused space for a new data block group. It's important to not use the mixed block groups feature as well because we later want to not have more space available for allocating data extents but still have enough metadata space free for creating the snapshot. Mount without space cache so that we can precisely fill all data space and unallocated space later (space cache v1 uses data block groups).

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick snapshot prealloc` declares tags `auto quick snapshot prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command "falloc" "-k"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_xfs_io_command "falloc" "-k"`; `_scratch_mkfs_sized $fs_size >>$seqres.full 2>&1`; `_scratch_mount $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -c "falloc -k 0 1914961920" $SCRATCH_MNT/foobar`; `$XFS_IO_PROG -c "pwrite -S 0xea -b 128K 0 128K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `md5sum $SCRATCH_MNT/foobar | _filter_scratch`; `_btrfs subvolume snapshot -r $SCRATCH_MNT $SCRATCH_MNT/snap`; `_scratch_unmount`; `_scratch_mount`; `echo "File digest after mounting the filesystem again:"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. The script records user-visible checksums, listings, device counters, capabilities, or byte dumps as evidence. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick snapshot prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
