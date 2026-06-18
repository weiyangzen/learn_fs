# sources/test-tools/xfstests/tests/generic/636

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/636`. Test invalid swap files. Empty swap file (only swap header) It is registered with `_begin_fstest auto quick swap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 32 source line(s).
- Harness registration: `_begin_fstest auto quick swap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`.
- Local shell functions: none visible.
- External `$here/src` helpers: `"$here/src/mkswap" "$SCRATCH_MNT/swap"`, `"$here/src/swapon" "$SCRATCH_MNT/swap"`.

## Control Flow

- Capability gating runs first through `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- Key operational lines include:
- `line 16: _require_scratch_swapfile`
- `line 20: _scratch_mkfs >> $seqres.full 2>&1`
- `line 21: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick swap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/636.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_swapfile`, `_require_test_program mkswap`, `_require_test_program swapon`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 636; swapon: Invalid argument'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
