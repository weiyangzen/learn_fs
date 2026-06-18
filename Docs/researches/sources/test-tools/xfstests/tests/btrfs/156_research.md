# sources/test-tools/xfstests/tests/btrfs/156

## Purpose

`sources/test-tools/xfstests/tests/btrfs/156` is btrfs fstests case `156`. It targets balance relocation behavior. Source comments describe the scenario as: Check if btrfs can correctly trim free space in block groups An ancient regression prevent btrfs from trimming free space inside existing block groups, if bytenr of block group starts beyond btrfs_super_block->total_bytes. However all bytenr in btrfs is in btrfs logical address space, where any bytenr in range [0, U64_MAX] is valid. Fixed by patch named "btrfs: Ensure btrfs_trim_fs can trim the whole fs". We need the allocated space to actually use that amount so the trim amount comes out correctly.  Because we mark free extents as TRIMMED we won't trim the free extents on the second fstrim and thus we'll get a trimmed bytes at <

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick trim balance` declares tags `auto quick trim balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_fstrim`, `_require_no_compress`, `_require_batched_discard "$SCRATCH_MNT"`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_fstrim`; `_check_minimal_fs_size $fs_size`; `_scratch_mkfs -b $fs_size -m single -d single > /dev/null`; `_scratch_mount`; `$XFS_IO_PROG -f -c "pwrite 0 $file_size" "$SCRATCH_MNT/file_$n" \`; `sync`; `_run_btrfs_balance_start $SCRATCH_MNT >> $seqres.full`; `rm $SCRATCH_MNT/file_*[13579] -f`; `trimmed=$($FSTRIM_PROG -v "$SCRATCH_MNT" | _filter_fstrim)`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick trim balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
