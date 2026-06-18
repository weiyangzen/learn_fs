# sources/test-tools/xfstests/tests/generic/729

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/729`. Trigger page faults in the same file during read and write This is generic/647 with an additional test that writes a memory-mapped page onto itself using direct I/O. The kernel will invalidate the page cache before carrying out the write, so filesystems that fault in the page and then carry out the direct I/O write with page faults disabled will never make any progress. It is registered with `_begin_fstest auto quick mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 40 source line(s).
- Harness registration: `_begin_fstest auto quick mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/mmap-rw-fault -2 $TEST_DIR/mmap-rw-fault.tmp`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.
- User-visible phase markers include:
- `line 35: echo "Silence is golden"`
- Key operational lines include:
- `line 17: _begin_fstest auto quick mmap`
- `line 24: rm -f $TEST_DIR/mmap-rw-fault.tmp`
- `line 33: _require_test_program mmap-rw-fault`
- `line 37: $here/src/mmap-rw-fault -2 $TEST_DIR/mmap-rw-fault.tmp`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick mmap`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/729.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_odirect`, `_require_test_program mmap-rw-fault`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 729; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
