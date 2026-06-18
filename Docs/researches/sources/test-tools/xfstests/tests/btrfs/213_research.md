# sources/test-tools/xfstests/tests/btrfs/213

## Purpose

`sources/test-tools/xfstests/tests/btrfs/213` is btrfs fstests case `213`. It targets balance relocation behavior. Source comments describe the scenario as: Test if canceling a running balance can lead to dead looping balance Create enough IO so that we need around 8 seconds to relocate it. Unmount and mount again the fs to clear any cached data and metadata, so that it's less likely balance has already finished when we try to cancel it below. Now balance should take at least $runtime seconds, we can cancel it at $runtime/4 to ensure a success cancel. It's possible that balance has already completed. It's unlikely but often it may happen due to virtualization, caching and other factors, so ignore any error about no balance currently running. Now check if we can finish relocating metadata, which should finish very

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto balance` declares tags `auto balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_xfs_io_command pwrite -D`, `_notrun "balance finished before we could cancel it"`; local shell helpers: `_cleanup()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `rm -f $tmp.*`; `_require_scratch`; `_require_xfs_io_command pwrite -D`; `"btrfs: reloc: clear DEAD_RELOC_TREE bit for orphan roots to prevent runaway balance"`; `_scratch_mkfs >> $seqres.full`; `_scratch_mount`; `max_space=$(_get_total_space $SCRATCH_MNT)`; `$TIMEOUT_PROG 8s $XFS_IO_PROG -f -c "pwrite -D -b 1M 0 $max_space" \`; `_scratch_cycle_mount`; `_run_btrfs_balance_start -d --bg "$SCRATCH_MNT"`; `$BTRFS_UTIL_PROG balance cancel "$SCRATCH_MNT" 2>&1 | grep -iq 'not in progress'`; `_notrun "balance finished before we could cancel it"`; `$BTRFS_UTIL_PROG balance start -m "$SCRATCH_MNT" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

It may be slow or disruptive because it reformats scratch storage and may use fault injection or degraded-device mounts.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
