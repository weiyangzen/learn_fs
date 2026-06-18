# sources/test-tools/xfstests/tests/btrfs/146

## Purpose

`sources/test-tools/xfstests/tests/btrfs/146` is btrfs fstests case `146`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Open a file several times, write to it, fsync on all fds and make sure that they all return 0. Change the device to start throwing errors. Write again on all fds and fsync on all fds. Ensure that we get errors on all of them. Then fsync on all one last time and verify that all return 0. bring up dmerror device Replace first device with error-test device Build a filesystem with 2 devices that stripes the data across both devices, but mirrors metadata across both. Then, make one of the devices fail and test what it does. How much do we need to write? We need to hit all of the stripes. btrfs uses a

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick eio raid` declares tags `auto quick eio raid`; environment gates are expressed through `_require*` helpers. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmerror`; requirements: `_require_scratch`, `_require_scratch_dev_pool`, `_require_dm_target error`, `_require_test_program fsync-err`, `_require_test_program dmerror`, `_require_fs_space $SCRATCH_MNT $write_kb`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -rf $tmp.* $testdir`; `_dmerror_cleanup`; `_require_scratch`; `_require_scratch_dev_pool`; `_require_test_program fsync-err`; `_require_test_program dmerror`; `_dmerror_init`; `_scratch_mount`; `number_of_devices=\`echo $SCRATCH_DEV_POOL | wc -w\``; `write_kb=$(($number_of_devices * 2048))`; `testfile=$SCRATCH_MNT/fsync-err-test`; `SCRATCH_DEV=$old_SCRATCH_DEV`; `$here/src/fsync-err -b $(($write_kb * 1024)) -d "$here/src/dmerror $seq" $testfile`; `_dmerror_load_working_table`; `_repair_scratch_fs >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick eio raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
