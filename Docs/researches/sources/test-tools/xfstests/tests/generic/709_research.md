# sources/test-tools/xfstests/tests/generic/709

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/709`. Can we use exchangerange to make the quota accounting incorrect? It is registered with `_begin_fstest auto quick fiexchange quota`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 54 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange quota`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/quota`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, `_require_scratch`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 34: echo before exchangerange >> $seqres.full`
- `line 46: echo after exchangerange >> $seqres.full`
- Key operational lines include:
- `line 16: _require_xfs_io_command exchangerange`
- `line 24: _scratch_mkfs > $seqres.full`
- `line 29: $XFS_IO_PROG -f -c 'pwrite -S 0x58 0 256k -b 1m' $SCRATCH_MNT/a >> $seqres.full`
- `line 31: $XFS_IO_PROG -f -c 'pwrite -S 0x59 0 64k -b 64k' -c 'truncate 256k' $SCRATCH_MNT/b >> $seqres.full`
- `line 34: echo before exchangerange >> $seqres.full`
- `line 36: stat $SCRATCH_MNT/* >> $seqres.full`
- `line 42: $XFS_IO_PROG -c "exchangerange $SCRATCH_MNT/b" $SCRATCH_MNT/a &> $tmp.swap`
- `line 46: echo after exchangerange >> $seqres.full`
- `line 48: stat $SCRATCH_MNT/* >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange quota`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/quota`), and the golden-output file `sources/test-tools/xfstests/tests/generic/709.out` (3 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_user`, `_require_nobody`, `_require_quota`, `_require_xfs_quota`, `_require_scratch`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 3 line(s); its first visible signals are: 'QA output created by 709; Comparing user usage; Comparing group usage'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
