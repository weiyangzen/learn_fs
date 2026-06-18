# sources/test-tools/xfstests/tests/btrfs/132

## Purpose

`sources/test-tools/xfstests/tests/btrfs/132` is btrfs fstests case `132`. It targets the btrfs feature area named by its fstests tags. Source comments describe the scenario as: Check if false ENOSPC will happen when parallel buffer write happens The problem is caused by incorrect metadata reservation for any buffered write whose max extent size is not 128M (including compression and in-band dedupe). Use small filesystem to trigger the bug more easily It's highly recommened to run this test case with MKFS_OPTIONS="-n 64k" to further increase the possibility Since the false ENOSPC happens due to incorrect metadata reservation, larger nodesize and small fs will make it much easier to reproduce Recommended to use MOUNT_OPTIONS="-o compress" to trigger the bug

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto enospc` declares tags `auto enospc`; environment gates are expressed through `_require*` helpers; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`; local shell helpers: `_cleanup()`, `loop_writer()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch`; `_scratch_mkfs_sized $((512 * 1024 * 1024)) >> $seqres.full 2>&1`; `_scratch_mount`; `loop_writer()`; `$XFS_IO_PROG -c "pwrite -b 8K $offset $len" $file > /dev/null`; `touch $SCRATCH_MNT/testfile`; `loop_writer 0 128M $SCRATCH_MNT/testfile &`; `loop_writer 128M 16M $SCRATCH_MNT/testfile &`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto enospc` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
