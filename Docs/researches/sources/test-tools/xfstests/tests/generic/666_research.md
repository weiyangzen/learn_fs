# sources/test-tools/xfstests/tests/generic/666

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/666`. Ensuring that copy on write in mmap mode to the source file when the CoW range covers delalloc blocks and regular shared blocks. (MMAP version of generic/293,295) - Create two files. - Truncate the first file. - Write the odd blocks of the first file. - Reflink the odd blocks of the first file into the second file. - Write the even blocks of the first file. - mmap CoW the first file across the halfway mark, starting with the regular extent. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone prealloc mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 64 source line(s).
- Harness registration: `_begin_fstest auto quick clone prealloc mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `testdir=$SCRATCH_MNT/test-$seq`
- `blksz=65536`
- `nr=64`
- `filesize=$((blksz * nr))`
- `cowoff=$((filesize / 4))`
- `cowsz=$((filesize / 2))`
- `mmapsz=$((cowoff + cowsz))`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 29: echo "Format and mount"`
- `line 36: echo "Create the original files"`
- `line 43: echo "Compare files"`
- `line 48: echo "mmap CoW across the transition"`
- `line 57: echo "Compare files"`
- Key operational lines include:
- `line 19: _begin_fstest auto quick clone prealloc mmap`
- `line 25: _require_scratch_reflink`
- `line 26: _require_scratch_delalloc`
- `line 27: _require_xfs_io_command "falloc"`
- `line 30: _scratch_mkfs > $seqres.full 2>&1`
- `line 31: _scratch_mount >> $seqres.full 2>&1`
- `line 40: _sweave_reflink_holes $blksz $nr $testdir/file1 $testdir/file3 >> $seqres.full`
- `line 41: _scratch_cycle_mount`
- `line 44: md5sum $testdir/file1 | _filter_scratch`
- `line 45: md5sum $testdir/file3 | _filter_scratch`
- `line 46: md5sum $testdir/file1.chk | _filter_scratch`
- `line 48: echo "mmap CoW across the transition"`
- `line 51: _sweave_reflink_holes_delalloc $blksz $nr $testdir/file1 >> $seqres.full`
- `line 52: mmapsz=$((cowoff + cowsz))`
- `line 53: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1 >> $seqres.full`
- `line 54: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file1.chk >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone prealloc mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/666.out` (12 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_scratch_delalloc`, `_require_xfs_io_command "falloc"`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 12 line(s); its first visible signals are: 'QA output created by 666; Format and mount; Create the original files; Compare files; b8a8a88d4c143f79900c4b4e79aa3e37  SCRATCH_MNT/test-666/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
