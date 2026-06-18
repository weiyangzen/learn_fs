# sources/test-tools/xfstests/tests/generic/707

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/707`. This is a test verifying whether the filesystem can gracefully handle modifying of a directory while it is being moved, in particular the cases where directory format changes It is registered with `_begin_fstest auto`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 70 source line(s).
- Harness registration: `_begin_fstest auto`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`, `_fixed_by_fs_commit udf f950fd052913 "udf: Protect rename against modification of moved directory"`.
- Local shell functions: `_cleanup`, `create_files`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `loops=$((100*TIME_FACTOR))`
- `files=500`
- `moves=500`
- `start_dir=$PWD`
- `BGPID=$!`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_fixed_by_fs_commit udf f950fd052913 "udf: Protect rename against modification of moved directory"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 45: echo -n > somewhatlongerfilename$i`
- `line 68: echo "Silence is golden"`
- Key operational lines include:
- `line 21: _scratch_mkfs >>$seqres.full 2>&1`
- `line 22: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/707.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_fixed_by_fs_commit udf f950fd052913 "udf: Protect rename against modification of moved directory"`.

## Risks and Edge Cases

- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 707; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
