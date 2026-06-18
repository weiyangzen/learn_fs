# sources/test-tools/xfstests/tests/btrfs/150

## Purpose

`sources/test-tools/xfstests/tests/btrfs/150` is btrfs fstests case `150`. It targets multi-device or RAID volume behavior, compression interactions, checksum, scrub, or read-repair paths, fault-injection or destructive-device conditions. Source comments describe the scenario as: This is a regression test which ends up with a kernel oops in btrfs. It occurs when btrfs's read repair happens while reading a compressed extent. The patch to fix it is Btrfs: fix kernel oops while reading compressed data It doesn't matter which compression algorithm we use. Create a file with all data being compressed Raid1 consists of two copies and btrfs decides which copy to read by reader's %pid.  Now we inject errors to copy #1 and copy #0 is good.  We want to read the bad copy to trigger read-repair.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick dangerous read_repair compress raid` declares tags `auto quick dangerous read_repair compress raid`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`, `./common/fail_make_request`; requirements: `_require_debugfs`, `_require_scratch`, `_require_fail_make_request`, `_require_scratch_dev_pool 2`; local shell helpers: `enable_io_failure()`, `disable_io_failure()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_fail_make_request`; `_require_scratch_dev_pool 2`; `_scratch_dev_pool_get 2`; `_allow_fail_make_request 100 1000 > /dev/null`; `_scratch_mount -ocompress`; `$XFS_IO_PROG -f -c "pwrite -W 0 8K" $SCRATCH_MNT/foobar | _filter_xfs_io`; `$XFS_IO_PROG -f -c "fadvise -d 0 8K" $SCRATCH_MNT/foobar`; `echo 1 > /proc/\$\$/make-it-fail`; `exec $XFS_IO_PROG -c \"pread 0 8K\" \$SCRATCH_MNT/foobar`; `_scratch_dev_pool_put`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Device identity, missing-device state, degraded mounts, and balance/repair writes are part of the persistent test surface. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick dangerous read_repair compress raid` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts. Multi-device tests need enough disposable devices and can leave device scans cached if cleanup does not run. Compression, inline-extent thresholds, and page or sector size can change the exact layout being exercised. Fault-injection timing must hit the intended mirror or stripe; otherwise the bug path may not execute.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output.
