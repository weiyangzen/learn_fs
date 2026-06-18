# sources/test-tools/xfstests/tests/btrfs/123

## Purpose

`sources/test-tools/xfstests/tests/btrfs/123` is btrfs fstests case `123`. It targets quota-group accounting and limits, balance relocation behavior. Source comments describe the scenario as: Test if btrfs leaks qgroup numbers for data extents Due to balance code is doing trick tree block swap, which doing non-standard extent reference update, qgroup can't handle it correctly, and leads to corrupted qgroup numbers. Need to use inline extents to fill metadata rapidly create 64K inlined metadata, which will ensure there is a 2-level metadata. Even for maximum nodesize(64K) then a large data write to make the quota corruption obvious enough enable quota and rescan to get correct number now balance data block groups to corrupt qgroup

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick qgroup balance` declares tags `auto quick qgroup balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_qgroup_report`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_qgroup_report`; `_scratch_mkfs >/dev/null`; `_scratch_mount "-o max_inline=2048"`; `_pwrite_byte 0xcdcdcdcd 0 2k $SCRATCH_MNT/small_$i | _filter_xfs_io`; `_pwrite_byte 0xcdcdcdcd 0 32m $SCRATCH_MNT/large | _filter_xfs_io`; `sync`; `_btrfs quota enable $SCRATCH_MNT`; `_qgroup_rescan $SCRATCH_MNT`; `_run_btrfs_balance_start -d $SCRATCH_MNT >> $seqres.full`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick qgroup balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. fstests scratch checking validates filesystem and qgroup consistency after unmount.
