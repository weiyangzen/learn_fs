# sources/test-tools/xfstests/tests/generic/638

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/638`. This case mmaps several pages of a file, alloc pages, copy data with pages overlapping, e.g: +-----------------------+ | (copy) | | V +---------------+---------------+------------ |AAAA| ........ |AAAA| ... |AAAA|AAAA| +---------------+---------------+------------ | ^ | (copy) | +------------+ This's a regression test cover kernel commit: 4f06dd92b5d0 ("fuse: fix write deadlock") It is registered with `_begin_fstest auto quick rw mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 39 source line(s).
- Harness registration: `_begin_fstest auto quick rw mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_test_program "t_mmap_writev_overlap"`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/t_mmap_writev_overlap -b $pagesize -c 2 -l 64 $testfile`.
- Notable variables and constants:
- `pagesize=`getconf PAGE_SIZE``
- `testfile=$TEST_DIR/mmap-writev-overlap`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_test_program "t_mmap_writev_overlap"`.
- User-visible phase markers include:
- `line 36: echo "Silence is golden"`
- Key operational lines include:
- `line 23: _begin_fstest auto quick rw mmap`
- `line 29: _require_test_program "t_mmap_writev_overlap"`
- `line 32: testfile=$TEST_DIR/mmap-writev-overlap`
- `line 33: $XFS_IO_PROG -f -c "truncate 0" $testfile`
- `line 34: $here/src/t_mmap_writev_overlap -b $pagesize -c 2 -l 64 $testfile`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick rw mmap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/638.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_test_program "t_mmap_writev_overlap"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 638; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
