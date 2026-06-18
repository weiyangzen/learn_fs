# sources/test-tools/xfstests/tests/btrfs/190

## Purpose

`sources/test-tools/xfstests/tests/btrfs/190` is btrfs fstests case `190`. It targets quota-group accounting and limits, balance relocation behavior. Source comments describe the scenario as: A general test to validate that balance and qgroups work correctly when balance needs to be resumed on mount. and we need extra device as log device Create enough metadata for later balance Flush delalloc so that balance has work to do. Balance metadata so we will have at least one transaction committed with valid reloc tree, and hopefully another commit with orphan reloc tree. Test that no crashes happen or any other kind of failure. Don't trigger fsck here, as relocation get paused, at that transistent state, qgroup number may differ

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick replay balance qgroup recoveryloop` declares tags `auto quick replay balance qgroup recoveryloop`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmlogwrites`; requirements: `_require_scratch`, `_require_log_writes`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_log_writes_mkfs >> $seqres.full 2>&1`; `_log_writes_mount`; `$BTRFS_UTIL_PROG quota enable $SCRATCH_MNT >> $seqres.full`; `_qgroup_rescan $SCRATCH_MNT >> $seqres.full`; `_pwrite_byte 0xcd 0 $file_size $SCRATCH_MNT/file_$i > /dev/null`; `sync`; `_run_btrfs_balance_start -f -m $SCRATCH_MNT >> $seqres.full`; `_log_writes_unmount`; `_scratch_mount`; `_scratch_unmount`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Quota-group counters, limits, inherited qgroups, and rescan results are kernel-maintained metadata validated at unmount/check time. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick replay balance qgroup recoveryloop` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Qgroup tests are sensitive to delayed accounting, rescan completion, and checker support for quota validation.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
