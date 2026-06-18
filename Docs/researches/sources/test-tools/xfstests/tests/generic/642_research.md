# sources/test-tools/xfstests/tests/generic/642

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/642`. Run an extended attributes fsstress run with multiple threads to shake out bugs in the xattr code. It is registered with `_begin_fstest auto soak attr long_rw stress smoketest`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 49 source line(s).
- Harness registration: `_begin_fstest auto soak attr long_rw stress smoketest`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `nr_cpus=$((LOAD_FACTOR * 4))`
- `nr_ops=$((70000 * TIME_FACTOR))`
- `args=('-z' '-S' 'c')`

## Control Flow

- Capability gating runs first through `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 17: echo "Silence is golden."`
- Key operational lines include:
- `line 19: _scratch_mkfs > $seqres.full 2>&1`
- `line 20: _scratch_mount >> $seqres.full 2>&1`
- `line 35: for verb in getfattr listfattr; do`
- `line 41: args+=('-f' "setfattr=20")`
- `line 45: _run_fsstress "${args[@]}" -d $SCRATCH_MNT -n $nr_ops -p $nr_cpus`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto soak attr long_rw stress smoketest`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/642.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 642; Silence is golden.'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
