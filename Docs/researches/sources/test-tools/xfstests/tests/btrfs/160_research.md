# sources/test-tools/xfstests/tests/btrfs/160

## Purpose

`sources/test-tools/xfstests/tests/btrfs/160` is btrfs fstests case `160`. It targets multi-device or RAID volume behavior. Source comments describe the scenario as: Open a file and write to it and fsync. Then flip the data device to throw errors, write to it again and call sync. Close the file, reopen it and then call fsync on it. Is the error reported? bring up dmerror device Replace first device with error-test device How much do we need to write? We need to hit all of the stripes. btrfs uses a fixed 64k stripesize, so write enough to hit each one. In the case of compression, each 128K input data chunk will be compressed to 4K (because of the characters written are duplicate). Therefore we have to write (128K * 16) = 2048K to make sure every stripe can be hit.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick eio raid` declares tags `auto quick eio raid`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmerror`; requirements: `_require_scratch_dev_pool`, `_require_dm_target error`, `_require_fs_space $SCRATCH_MNT $write_kb`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_dmerror_cleanup`; `_require_scratch_dev_pool`; `_dmerror_init`; `old_SCRATCH_DEV=$SCRATCH_DEV`; `_scratch_mount`; `number_of_devices=\`echo $SCRATCH_DEV_POOL | wc -w\``; `write_kb=$(($number_of_devices * 2048))`; `testfile=$SCRATCH_MNT/fsync-open-after-err`; `$XFS_IO_PROG -c "pwrite -q 0 $datalen" -c fsync $testfile`; `_dmerror_load_error_table`; `$XFS_IO_PROG -c "pwrite -q 0 $datalen" -c sync $testfile`; `_dmerror_load_working_table`; `echo "The following fsync should fail with EIO:"`; `$XFS_IO_PROG -c fsync $testfile |& \`; `_filter_flakey_EIO "fsync: Input/output error"`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. The dm-flakey helper deliberately drops writes and remounts to force replay of whatever reached the btrfs log tree. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick eio raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The pass/fail signal depends on realistic crash semantics from dm-flakey and on metadata journaling being available. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
