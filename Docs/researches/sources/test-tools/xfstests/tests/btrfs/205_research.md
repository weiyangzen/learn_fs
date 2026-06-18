# sources/test-tools/xfstests/tests/btrfs/205

## Purpose

`sources/test-tools/xfstests/tests/btrfs/205` is btrfs fstests case `205`. It targets compression interactions. Source comments describe the scenario as: Test several scenarios of cloning operations where the source range includes inline extents. They used to not be supported on btrfs because their implementation was not straightforward, and therefore these operations used to fail with errno EOPNOTSUPP on older kernels. Support for this was added by a patch with the following subject: "Btrfs: implement full reflink support for inline extents" We want to create a compressed inline extent representing 4K of data for file foo1 and then clone it into a file without compression, and since compression implies datasum, cloning fails if the destination file has nodatasum. So skip the test if nodatasum is present in MOUNT_OPTIONS.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick clone compress prealloc` declares tags `auto quick clone compress prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/reflink`; requirements: `_require_scratch_reflink`, `_require_xfs_io_command "falloc" "-k"`, `_require_command "$CHATTR_PROG" chattr`, `_require_btrfs_fs_feature "no_holes"`, `_require_btrfs_mkfs_feature "no-holes"`, `_require_btrfs_no_nodatasum`; local shell helpers: `run_tests()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_reflink`; `_require_xfs_io_command "falloc" "-k"`; `_require_command "$CHATTR_PROG" chattr`; `_require_btrfs_fs_feature "no_holes"`; `_require_btrfs_mkfs_feature "no-holes"`; `$XFS_IO_PROG -c "pwrite -S 0xab 0 4K" \`; `-c "fsync" \`; `-c "pwrite -S 0xab 4K 124K" \`; `$XFS_IO_PROG -f -c "pwrite -S 0xcd 0 128K" $SCRATCH_MNT/bar1 | _filter_xfs_io`; `$XFS_IO_PROG -c "reflink $SCRATCH_MNT/foo1 0 128K 128K" $SCRATCH_MNT/bar1 \`; `$XFS_IO_PROG -f -c "pwrite -S 0xab 0 1000" \`; `_scratch_mount`; `_scratch_cycle_mount "compress"`; `_scratch_cycle_mount "nodatacow"`; `_scratch_unmount`; `_scratch_mkfs "-O no-holes" >>$seqres.full 2>&1`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick clone compress prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Before/after checksums must match across remount, balance, or receive.
