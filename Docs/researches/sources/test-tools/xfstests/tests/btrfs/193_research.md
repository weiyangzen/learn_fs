# sources/test-tools/xfstests/tests/btrfs/193

## Purpose

`sources/test-tools/xfstests/tests/btrfs/193` is btrfs fstests case `193`. It targets quota-group accounting and limits. Source comments describe the scenario as: Test if btrfs is going to leak qgroup reserved data space when falloc on multiple holes fails. The fix is titled: "btrfs: qgroup: Fix the wrong target io_tree when freeing reserved data space" Create a file with the following layout: 0         128M      256M      384M |  Hole   |4K| Hole |4K| Hole | The total hole size will be 384M - 8k Falloc 0~384M range, it's going to fail due to the qgroup limit Ensure above delete reaches disk and free some space

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup enospc limit prealloc` declares tags `auto quick qgroup enospc limit prealloc`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command falloc`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_xfs_io_command falloc`; `_scratch_mkfs > /dev/null`; `_scratch_mount`; `$BTRFS_UTIL_PROG quota enable "$SCRATCH_MNT" > /dev/null`; `_qgroup_rescan "$SCRATCH_MNT" > /dev/null`; `$BTRFS_UTIL_PROG qgroup limit -e 256M "$SCRATCH_MNT"`; `truncate -s 384m "$SCRATCH_MNT/file"`; `$XFS_IO_PROG -c "pwrite 128m 4k" -c "pwrite 256m 4k" \`; `$XFS_IO_PROG -c "falloc 0 384m" "$SCRATCH_MNT/file" | _filter_xfs_io_error`; `rm -f "$SCRATCH_MNT/file"`; `sync`; `$XFS_IO_PROG -f -c "pwrite 0 192m" "$SCRATCH_MNT/file" | _filter_xfs_io`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup enospc limit prealloc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
