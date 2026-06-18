# sources/test-tools/xfstests/tests/btrfs/153

## Purpose

`sources/test-tools/xfstests/tests/btrfs/153` is btrfs fstests case `153`. It targets quota-group accounting and limits. Source comments describe the scenario as: Test for leaking quota reservations on preallocated files.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup limit preallocrw` declares tags `auto quick qgroup limit preallocrw`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_qgroup_report`, `_require_xfs_io_command "falloc"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_qgroup_report`; `_require_xfs_io_command "falloc"`; `_scratch_mkfs >/dev/null`; `_scratch_mount`; `_btrfs quota enable $SCRATCH_MNT`; `_qgroup_rescan $SCRATCH_MNT`; `_btrfs qgroup limit 100M 0/5 $SCRATCH_MNT`; `testfile1=$SCRATCH_MNT/testfile1`; `testfile2=$SCRATCH_MNT/testfile2`; `$XFS_IO_PROG -fc "falloc 0 80M" $testfile1`; `$XFS_IO_PROG -fc "pwrite 0 80M" $testfile1 > /dev/null`; `$XFS_IO_PROG -fc "falloc 0 19M" $testfile2`; `$XFS_IO_PROG -fc "pwrite 0 19M" $testfile2 > /dev/null`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup limit preallocrw` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. fstests scratch checking validates filesystem and qgroup consistency after unmount.
