# sources/test-tools/xfstests/tests/btrfs/142

## Purpose

`sources/test-tools/xfstests/tests/btrfs/142` is btrfs fstests case `142`. It targets multi-device or RAID volume behavior, checksum, scrub, or read-repair paths. Source comments describe the scenario as: Regression test for btrfs DIO read's repair during read without checksum. Commit 2dabb3248453 ("Btrfs: Direct I/O read: Work on sectorsized blocks") introduced this regression.  It'd cause 'Segmentation fault' error. The upstream fix is commit 97bf5a5589aa ("Btrfs: fix segmentation fault when doing dio read") step 1, create a raid1 btrfs which contains one 128k file. make sure data is written to the start position of the data chunk step 2, corrupt the first 64k of stripe #1 step 3, 128k dio read (this read can repair bad copy) check if the repair works

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick read_repair raid` declares tags `auto quick read_repair raid`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/dmdust`; requirements: `_require_scratch_dev_pool 2`, `_require_dm_target dust`, `_require_btrfs_command inspect-internal dump-tree`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch_dev_pool 2`; `_require_dm_target dust`; `_require_btrfs_command inspect-internal dump-tree`; `_scratch_dev_pool_get 2`; `echo "step 1......mkfs.btrfs" >>$seqres.full`; `_scratch_mount -o nodatasum $(_btrfs_no_v1_cache_opt)`; `$XFS_IO_PROG -f -d -c "pwrite -S 0xaa -b 128K 0 128K" "$SCRATCH_MNT/foobar" |\`; `$XFS_IO_PROG -d -c "pwrite -S 0xbb -b 64K $physical 64K" "$SCRATCH_DEV" > /dev/null`; `_mount_dust`; `$DMSETUP_PROG message dust-test.$seq 0 enable`; `_btrfs_direct_read_on_mirror $stripe 2 "$SCRATCH_MNT/foobar" 0 128K`; `_cleanup_dust`; `$XFS_IO_PROG -c "pread -v -b 512 $physical 512" "$SCRATCH_DEV" |`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick read_repair raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
