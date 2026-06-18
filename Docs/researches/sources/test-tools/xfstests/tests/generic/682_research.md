# sources/test-tools/xfstests/tests/generic/682

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/682`. Ensure that unprivileged userspace hits EDQUOT while moving files into a directory when the directory's quota limits have been exceeded. Regression test for commit: 41667260bc84 ("xfs: reserve quota for target dir expansion when renaming files") It is registered with `_begin_fstest auto quick quota`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 79 source line(s).
- Harness registration: `_begin_fstest auto quick quota`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/quota`.
- Capability and skip gates: `_require_quota`, `_require_user`, `_require_scratch`.
- Local shell functions: `_filter_mv_output`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `blocksize=$(_get_dir_block_size $SCRATCH_MNT)`
- `scratchdir=$SCRATCH_MNT/dir`
- `scratchfile=$SCRATCH_MNT/file`
- `stagedir=$SCRATCH_MNT/staging`
- `total_size=$((blocksize * 2))`
- `dirents=$((total_size / 255))`
- `name=$(printf "x%0254d" $i)`
- `name=$(printf "y%0254d" $i)`

## Control Flow

- Capability gating runs first through `_require_quota`, `_require_user`, `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- User-visible phase markers include:
- `line 48: echo "set up quota" >> $seqres.full`
- `line 52: echo $(ls $scratchdir | wc -l) files in $scratchdir >> $seqres.full`
- `line 64: echo "fail quota" >> $seqres.full`
- `line 73: echo $(ls $scratchdir | wc -l) files in $scratchdir >> $seqres.full`
- `line 77: echo Silence is golden`
- Key operational lines include:
- `line 27: _scratch_mkfs > "$seqres.full" 2>&1`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick quota`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/quota`), and the golden-output file `sources/test-tools/xfstests/tests/generic/682.out` (3 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_quota`, `_require_user`, `_require_scratch`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 3 line(s); its first visible signals are: "QA output created by 682; mv: cannot overwrite 'SCRATCH_MNT/dir/yXXX': Disk quota exceeded; Silence is golden". Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
