# sources/test-tools/xfstests/tests/generic/657

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/657`. Ensuring that copy on write in mmap mode works when the CoW range originally covers multiple extents. (MMAP version of generic/185,183) - Create two files - Reflink the odd blocks of the first file into a third file. - Reflink the even blocks of the second file into the third file. - mmap CoW across the halfway mark. - Check that the files are now different where we say they're different. It is registered with `_begin_fstest auto quick clone mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 68 source line(s).
- Harness registration: `_begin_fstest auto quick clone mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`.
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

- Capability gating runs first through `_require_scratch_reflink`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 23: echo "Format and mount"`
- `line 30: echo "Create the original files"`
- `line 46: echo "Compare files"`
- `line 52: echo "mmap CoW across the transition"`
- `line 60: echo "Compare files"`
- Key operational lines include:
- `line 15: _begin_fstest auto quick clone mmap`
- `line 21: _require_scratch_reflink`
- `line 24: _scratch_mkfs > $seqres.full 2>&1`
- `line 25: _scratch_mount >> $seqres.full 2>&1`
- `line 37: _reflink_range $testdir/file1 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- `line 41: _reflink_range $testdir/file2 $((blksz * f)) $testdir/file3 $((blksz * f)) $blksz >> $seqres.full`
- `line 44: _scratch_cycle_mount`
- `line 47: md5sum $testdir/file1 | _filter_scratch`
- `line 48: md5sum $testdir/file2 | _filter_scratch`
- `line 49: md5sum $testdir/file3 | _filter_scratch`
- `line 50: md5sum $testdir/file3.chk | _filter_scratch`
- `line 52: echo "mmap CoW across the transition"`
- `line 55: mmapsz=$((cowoff + cowsz))`
- `line 56: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3 >> $seqres.full`
- `line 57: _mwrite_byte 0x63 $cowoff $cowsz $mmapsz $testdir/file3.chk >> $seqres.full`
- `line 58: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick clone mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/657.out` (14 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`.

## Risks and Edge Cases

- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 14 line(s); its first visible signals are: 'QA output created by 657; Format and mount; Create the original files; Compare files; bdbcf02ee0aa977795a79d25fcfdccb1  SCRATCH_MNT/test-657/file1'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
