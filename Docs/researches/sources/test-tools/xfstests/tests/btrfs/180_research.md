# sources/test-tools/xfstests/tests/btrfs/180

## Purpose

`sources/test-tools/xfstests/tests/btrfs/180` is btrfs fstests case `180`. It targets quota-group accounting and limits. Source comments describe the scenario as: Test if btrfs hits EDQUOT without reclaiming already freed extents when quota is enabled. This bug is going to be fxied by a patch for kernel titled "btrfs: qgroup: Make qgroup async transaction commit more aggressive" Commit transaction to reflect the quota usage Without the kernel fix, this will trigger EDQUOT.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup limit prealloc` declares tags `auto quick qgroup limit prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command falloc`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_xfs_io_command falloc`; `_scratch_mkfs > /dev/null`; `_scratch_mount`; `$BTRFS_UTIL_PROG quota enable "$SCRATCH_MNT" > /dev/null`; `_qgroup_rescan "$SCRATCH_MNT" > /dev/null`; `$BTRFS_UTIL_PROG qgroup limit -e 1G "$SCRATCH_MNT"`; `$XFS_IO_PROG -f -c "falloc 0 900M" "$SCRATCH_MNT/padding"`; `sync`; `rm -f "$SCRATCH_MNT/padding"`; `_pwrite_byte 0xcd 0 512M "$SCRATCH_MNT/real_file" | _filter_xfs_io`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup limit prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
