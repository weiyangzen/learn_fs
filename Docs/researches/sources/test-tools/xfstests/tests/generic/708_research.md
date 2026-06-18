# sources/test-tools/xfstests/tests/generic/708

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/708`. Test iomap direct_io partial writes. Create a reasonably large file, then run a program which mmaps it, touches the first page, then dio writes it to a second file. This can result in a page fault reading from the mmapped dio write buffer and thus the iomap direct_io partial write codepath. It is registered with `_begin_fstest quick auto mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 36 source line(s).
- Harness registration: `_begin_fstest quick auto mmap`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit btrfs b73a6fd1b1ef "btrfs: split partial dio bios before submit"`, `_require_test`, `_require_odirect`, `_require_test_program dio-buf-fault`.
- Local shell functions: none visible.
- External `$here/src` helpers: `$here/src/dio-buf-fault $src $dst > /dev/null || _fail "failed doing the dio copy"`.
- Notable variables and constants:
- `src=$TEST_DIR/dio-buf-fault-$seq.src`
- `dst=$TEST_DIR/dio-buf-fault-$seq.dst`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit btrfs b73a6fd1b1ef "btrfs: split partial dio bios before submit"`, `_require_test`, `_require_odirect`, `_require_test_program dio-buf-fault`.
- User-visible phase markers include:
- `line 28: echo "Silence is golden"`
- Key operational lines include:
- `line 15: _begin_fstest quick auto mmap`
- `line 30: $XFS_IO_PROG -fc "pwrite -q -S 0xcd 0 $((2 * 1024 * 1024))" $src`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest quick auto mmap`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/708.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit btrfs b73a6fd1b1ef "btrfs: split partial dio bios before submit"`, `_require_test`, `_require_odirect`, `_require_test_program dio-buf-fault`.

## Risks and Edge Cases

- Direct/AIO coverage depends on alignment, device logical block size, page size, and filesystem direct-I/O semantics.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 708; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
