# sources/test-tools/xfstests/tests/generic/670

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/670`. Test for races or FS corruption between reflink and mmap reading the target file. (MMAP version of generic/164,165) It is registered with `_begin_fstest auto clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 74 source line(s).
- Harness registration: `_begin_fstest auto clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_cp_reflink`.
- Local shell functions: `fbytes`, `reader`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `finished_file=$tmp.finished`
- `loops=512`
- `nr_loops=$((loops - 1))`
- `blksz=65536`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_cp_reflink`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 21: echo "Format and mount"`
- `line 34: echo "Initialize files"`
- `line 35: echo >> $seqres.full`
- `line 54: echo "Reflink and mmap reread the files!"`
- `line 68: echo "Finished reflinking"`
- Key operational lines include:
- `line 10: _begin_fstest auto clone mmap`
- `line 18: _require_scratch_reflink`
- `line 19: _require_cp_reflink`
- `line 22: _scratch_mkfs > $seqres.full 2>&1`
- `line 23: _scratch_mount >> $seqres.full 2>&1`
- `line 38: _cp_reflink $testdir/file1 $testdir/file3`
- `line 39: _scratch_cycle_mount`
- `line 49: while [ ! -e $finished_file ]; do`
- `line 54: echo "Reflink and mmap reread the files!"`
- `line 58: _reflink_range $testdir/file1 $((i * blksz)) \`
- `line 63: _reflink_range $testdir/file2 $((i * blksz)) \`
- `line 68: echo "Finished reflinking"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto clone mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/670.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_cp_reflink`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: 'QA output created by 670; Format and mount; Initialize files; Reflink and mmap reread the files!; Finished reflinking'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
