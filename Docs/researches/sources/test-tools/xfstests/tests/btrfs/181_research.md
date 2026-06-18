# sources/test-tools/xfstests/tests/btrfs/181

## Purpose

`sources/test-tools/xfstests/tests/btrfs/181` is btrfs fstests case `181`. It targets balance relocation behavior. Source comments describe the scenario as: Test if btrfs will commit too many transactions for nothing and cause performance regression during balance. This bug is going to be fixed by a patch for kernel title "btrfs: don't end the transaction for delayed refs in throttle" Create some small files to take up enough metadata reserved space Commit the fs so we can get a stable super generation Since the fs is pretty small, we should have only 1 small metadata chunk and one tiny system chunk. Relocating such small chunks only needs 6 commits for each, thus 12 commits for 2 chunks.

## Important APIs, Types, and Functions

This is an executable bash test, not a library module. Key interfaces are: `_begin_fstest auto quick balance` declares tags `auto quick balance`; environment gates are expressed through `_require*` helpers; btrfs userspace operations are issued through `$BTRFS_UTIL_PROG` or `_btrfs`; data I/O and fsync/preallocation paths are driven by `$XFS_IO_PROG` and `_pwrite_byte`. sourced helpers: `./common/preamble`, `./common/filter`; requirements: `_require_scratch`, `_require_btrfs_command inspect-internal dump-super`; local shell helpers: `get_super_gen()`.

## Control Flow

The script follows the normal fstests lifecycle: source helpers, declare feature tags, gate the environment, create or mount scratch storage, run the btrfs workload, and leave verification to explicit checks plus fstests teardown. The main source-level command path is: `_require_scratch`; `_require_btrfs_command inspect-internal dump-super`; `_scratch_mkfs > /dev/null`; `_scratch_mount`; `local ret=$($BTRFS_UTIL_PROG inspect dump-super "$SCRATCH_DEV" |\`; `$BTRFS_UTIL_PROG subvolume create "$SCRATCH_MNT/subvol" > /dev/null`; `_pwrite_byte 0xcd 0 1K "$SCRATCH_MNT/subvol/file_$i" > /dev/null`; `sync`; `_run_btrfs_balance_start -m $SCRATCH_MNT >> $seqres.full`; `echo "balance committed too many transactions"`; `echo "super generation before balance: ${before_gen}"`; `echo "super generation after balance:  ${after_gen}"`; `echo "super generation before balance: ${before_gen}" >> $seqres.full`; `echo "super generation after balance:  ${after_gen}" >> $seqres.full`.

## State and Persistence Behavior

The durable state under test lives on `$SCRATCH_MNT` and, for device-pool tests, on the scratch block devices themselves. Subvolume roots, read-only snapshots, deleted snapshot orphans, and directory entries are persisted across remounts. Cleanup code removes temporary files, tears down dm targets or device-pool state when present, and returns control to fstests scratch checking.

## Dependencies and Integration Points

Integration is through xfstests common helpers, btrfs-progs, xfs_io helper commands, optional dm targets, optional loop/debugfs/sysfs facilities, and the scratch filesystem checker. The test is selected by tags `auto quick balance` and therefore participates in fstests quick/auto/dangerous/feature subsets according to those labels.

## Risks and Edge Cases

The main risk is environmental: missing fstests helpers, unsupported btrfs features, or changed userspace output can turn the test into a notrun or golden-output mismatch.

## Test Signals

A matching `.out` file provides the golden stdout contract for stable messages and filtered command output. Most success is absence of unexpected output, ending with `Silence is golden`.
