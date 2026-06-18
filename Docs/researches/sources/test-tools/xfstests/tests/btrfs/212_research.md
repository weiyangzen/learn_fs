# sources/test-tools/xfstests/tests/btrfs/212

## Purpose

`sources/test-tools/xfstests/tests/btrfs/212` is btrfs fstests case `212`. It targets balance relocation behavior, fault-injection or destructive-device conditions. Source comments describe the scenario as: Test if unmounting a fs with balance canceled can lead to crash. This needs CONFIG_BTRFS_DEBUG compiled, which adds extra unmount time self-test

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto balance dangerous` declares tags `auto balance dangerous`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`; local shell helpers: `_cleanup()`, `balance_workload()`, `cancel_workload()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `kill $balance_pid &> /dev/null`; `$BTRFS_UTIL_PROG balance cancel $SCRATCH_MNT &> /dev/null`; `rm -f $tmp.*`; `_require_scratch`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`; `balance_workload()`; `_run_btrfs_balance_start &> /dev/null`; `balance_workload &`; `balance_pid=$!`; `kill $balance_pid`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto balance dangerous` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
