# sources/test-tools/xfstests/tests/btrfs/126

## Purpose

`sources/test-tools/xfstests/tests/btrfs/126` is btrfs fstests case `126`. It targets quota-group accounting and limits. Source comments describe the scenario as: Regression test for leaking data space after hitting EDQUOTA This test requires specific data space usage, skip if we have compression enabled. Use enospc_debug mount option to trigger restrict space info check The amount of written data may change due to different nodesize at mkfs time, so redirect stdout to seqres.full. Also, EDQUOTA is expected, which can't be redirected due to the limitation of _filter_xfs_io, so golden output will include EDQUOTA error message Fstests will umount the fs, and at umount time, kernel warning will be triggered

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup limit` declares tags `auto quick qgroup limit`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_qgroup_report`, `_require_no_compress`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_qgroup_report`; `_scratch_mkfs >/dev/null`; `_scratch_mount "-o enospc_debug"`; `_btrfs quota enable $SCRATCH_MNT`; `_qgroup_rescan $SCRATCH_MNT`; `_btrfs qgroup limit 512K 0/5 $SCRATCH_MNT`; `_pwrite_byte 0xcdcdcdcd 0 1M $SCRATCH_MNT/test_file 2>&1 >> $seqres.full | \`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup limit` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
