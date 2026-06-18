# sources/test-tools/xfstests/tests/generic/678

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/678`. Test doing a read, with io_uring, over a file range that includes multiple extents. The read operation triggers page faults when accessing all pages of the read buffer except for the pages corresponding to the first extent. Then verify that the operation results in reading all the extents and returns the correct data. It is registered with `_begin_fstest auto quick io_uring`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 37 source line(s).
- Harness registration: `_begin_fstest auto quick io_uring`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_test`, `_require_odirect`, `_require_io_uring`, `_require_test_program uring_read_fault`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `$here/src/uring_read_fault $TEST_DIR/uring_read_fault.tmp`.

## Control Flow

- Capability gating runs first through `_require_test`, `_require_odirect`, `_require_io_uring`, `_require_test_program uring_read_fault`.
- User-visible phase markers include:
- `line 36: echo "Silence is golden"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick io_uring`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/678.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_odirect`, `_require_io_uring`, `_require_test_program uring_read_fault`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 678; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
