# sources/test-tools/xfstests/tests/generic/630

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/630`. Make sure that mmap and file writers racing with FIDEDUPERANGE cannot write to the file after the dedupe prep function has decided that the file contents are identical and we can therefore go ahead with the remapping. It is registered with `_begin_fstest auto quick rw dedupe clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 35 source line(s).
- Harness registration: `_begin_fstest auto quick rw dedupe clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_dedupe`, `_require_test_program "deduperace"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/deduperace -c $SCRATCH_MNT -n $nr_ops`, `$here/src/deduperace -c $SCRATCH_MNT -n $nr_ops -w`.
- Notable variables and constants:
- `nr_ops=$((TIME_FACTOR * 10000))`

## Control Flow

- Capability gating runs first through `_require_scratch_dedupe`, `_require_test_program "deduperace"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 32: echo Silence is golden.`
- Key operational lines include:
- `line 12: _begin_fstest auto quick rw dedupe clone mmap`
- `line 17: _require_scratch_dedupe`
- `line 18: _require_test_program "deduperace"`
- `line 23: _scratch_mkfs > $seqres.full`
- `line 24: _scratch_mount`
- `line 27: $here/src/deduperace -c $SCRATCH_MNT -n $nr_ops`
- `line 30: $here/src/deduperace -c $SCRATCH_MNT -n $nr_ops -w`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rw dedupe clone mmap`, common helper libraries (`./common/preamble`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/630.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_dedupe`, `_require_test_program "deduperace"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 630; Silence is golden.'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
