# sources/test-tools/xfstests/tests/btrfs/195

## Purpose

`sources/test-tools/xfstests/tests/btrfs/195` is btrfs fstests case `195`. It targets multi-device or RAID volume behavior, balance relocation behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Test raid profile conversion. It's sufficient to test all dest profiles as source profiles just rely on being able to read the data and metadata. Zoned btrfs only supports SINGLE profile Load up the available configs $nr_dev_min:$data:$metadata:$data_convert:$metadata_convert Create random filesystem with 20k write ops

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto volume balance scrub raid` declares tags `auto volume balance scrub raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch_dev_pool 4`, `_require_non_zoned_device "${SCRATCH_DEV}"`; local shell helpers: `run_testcase()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 4`; `_require_non_zoned_device "${SCRATCH_DEV}"`; `_btrfs_get_profile_configs`; `"4:single:raid1"`; `"4:single:raid0"`; `_scratch_mount`; `_run_btrfs_balance_start -f -dconvert=$dst_type $SCRATCH_MNT >> $seqres.full`; `$BTRFS_UTIL_PROG scrub start -B $SCRATCH_MNT >>$seqres.full 2>&1`; `_scratch_unmount`; `_check_btrfs_filesystem $SCRATCH_DEV`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto volume balance scrub raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`. A foreground scrub must complete without reported errors.
