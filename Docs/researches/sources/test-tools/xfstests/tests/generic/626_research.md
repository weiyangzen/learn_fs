# sources/test-tools/xfstests/tests/generic/626

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/626`. Test RENAME_WHITEOUT on filesystem without space to create one more inodes. This is a regression test for kernel commit: 6b4b8e6b4ad8 ("ext4: ext4: fix bug for rename with RENAME_WHITEOUT") It is registered with `_begin_fstest auto quick rename enospc`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 56 source line(s).
- Harness registration: `_begin_fstest auto quick rename enospc`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/populate`, `./common/renameat2`.
- Capability and skip gates: `_require_scratch`, `_require_renameat2 whiteout`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/renameat2 -w $SCRATCH_MNT/srcfile$i $SCRATCH_MNT/dstfile$i >> $seqres.full 2>&1`.
- Notable variables and constants:
- `NR_FILE=$((4 * 64))`
- `nr_free=$(stat -f -c '%f' $SCRATCH_MNT)`
- `blksz="$(_get_block_size $SCRATCH_MNT)"`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_renameat2 whiteout`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 53: echo "Silence is golden"`
- Key operational lines include:
- `line 21: _require_renameat2 whiteout`
- `line 23: _scratch_mkfs_sized $((256 * 1024 * 1024)) >> $seqres.full 2>&1`
- `line 24: _scratch_mount`
- `line 32: nr_free=$(stat -f -c '%f' $SCRATCH_MNT)`
- `line 45: $here/src/renameat2 -w $SCRATCH_MNT/srcfile$i $SCRATCH_MNT/dstfile$i >> $seqres.full 2>&1`
- `line 47: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rename enospc`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/populate`, `./common/renameat2`), and the golden-output file `sources/test-tools/xfstests/tests/generic/626.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_renameat2 whiteout`.

## Risks and Edge Cases

- ENOSPC-sensitive timing can vary with allocator geometry, free-space accounting, delayed allocation, and background reservations.
- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 626; Silence is golden'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
