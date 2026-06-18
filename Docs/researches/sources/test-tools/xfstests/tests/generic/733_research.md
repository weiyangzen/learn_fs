# sources/test-tools/xfstests/tests/generic/733

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/733`. Race file reads with a very slow reflink operation to see if the reads actually complete while the reflink is ongoing. This is a functionality test for XFS commit 14a537983b22 "xfs: allow read IO and FICLONE to run concurrently" and for BTRFS commit 5d6f0e9890ed "btrfs: stop locking the source extent range during reflink". It is registered with `_begin_fstest auto clone punch`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 93 source line(s).
- Harness registration: `_begin_fstest auto clone punch`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/attr`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`, `_require_test_program "t_reflink_read_race"`, `_require_command "$TIMEOUT_PROG" timeout`, `_fixed_by_fs_commit btrfs 5d6f0e9890ed "btrfs: stop locking the source extent range during reflink"`, `_fixed_by_fs_commit xfs 14a537983b22 "xfs: allow read IO and FICLONE to run concurrently"`, `_notrun "Insufficient space for stress test; would only create $blocks_needed extents."`.
- Local shell functions: `calc_space`.
- External `$here/src` helpers: `"$here/src/punch-alternating" "$testdir/file1" >> "$seqres.full"`, `{ $here/src/t_reflink_read_race "$testdir/file1" "$testdir/file2" \`.
- Notable variables and constants:
- `testdir="$SCRATCH_MNT/test-$seq"`
- `blocks_needed=$(( 2 ** (fnr + 1) ))`
- `space_needed=$((blocks_needed * blksz * 5 / 4))`
- `free_blocks=$(stat -f -c '%a' "$testdir")`
- `blksz=$(_get_file_block_size "$testdir")`
- `space_avail=$((free_blocks * blksz))`
- `off=$(( (2 ** fnr) * blksz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`, `_require_test_program "t_reflink_read_race"`, plus 4 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 35: echo "Format and mount"`
- `line 49: echo "Create a many-block file"`
- `line 64: echo "fnr=$fnr" >> $seqres.full`
- `line 66: echo "Reflink the big file"`
- `line 84: echo "Could not set up program"`
- `line 86: echo "test completed successfully"`
- Key operational lines include:
- `line 21: _require_scratch_reflink`
- `line 22: _require_cp_reflink`
- `line 25: _require_test_program "t_reflink_read_race"`
- `line 26: _require_command "$TIMEOUT_PROG" timeout`
- `line 29: "btrfs: stop locking the source extent range during reflink"`
- `line 36: _scratch_mkfs > "$seqres.full" 2>&1`
- `line 37: _scratch_mount >> "$seqres.full" 2>&1`
- `line 51: free_blocks=$(stat -f -c '%a' "$testdir")`
- `line 59: $XFS_IO_PROG -f -c "pwrite -S 0x61 -b 4194304 $off $off" "$testdir/file1" >> "$seqres.full"`
- `line 62: $TIMEOUT_PROG 1s cp --reflink=always "$testdir/file1" "$testdir/garbage" || break`
- `line 80: { $here/src/t_reflink_read_race "$testdir/file1" "$testdir/file2" \`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone punch`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/attr`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/733.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_xfs_io_command "fpunch"`, `_require_test_program "punch-alternating"`, `_require_test_program "t_reflink_read_race"`, `_require_command "$TIMEOUT_PROG" timeout`, `_fixed_by_fs_commit btrfs 5d6f0e9890ed "btrfs: stop locking the source extent range during reflink"`, `_fixed_by_fs_commit xfs 14a537983b22 "xfs: allow read IO and FICLONE to run concurrently"`, plus 1 more.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: 'QA output created by 733; Format and mount; Create a many-block file; Reflink the big file; test completed successfully'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
