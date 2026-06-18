# sources/test-tools/xfstests/tests/generic/717

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/717`. Try invalid parameters to see if they fail. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 95 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test`, `_require_scratch`, `_require_chattr i`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test`, `_require_scratch`, `_require_chattr i`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 40: echo Immutable files`
- `line 44: echo Readonly files`
- `line 47: echo Directories`
- `line 50: echo Unaligned ranges`
- `line 53: echo file1 range entirely beyond EOF`
- `line 56: echo file2 range entirely beyond EOF`
- `line 59: echo Both ranges entirely beyond EOF`
- `line 62: echo file1 range crossing EOF`
- Key operational lines include:
- `line 23: _require_xfs_io_command exchangerange`
- `line 24: _require_xfs_io_command startupdate`
- `line 34: _scratch_mkfs >> $seqres.full`
- `line 35: _scratch_mount`
- `line 41: $XFS_IO_PROG -c 'chattr +i' -c "exchangerange $dir/b" $dir/a`
- `line 45: $XFS_IO_PROG -r -c "exchangerange $dir/b" $dir/a`
- `line 48: $XFS_IO_PROG -c "exchangerange $dir/b" $dir`
- `line 51: $XFS_IO_PROG -c "exchangerange -s 37 -d 61 -l 17 $dir/b" $dir/a`
- `line 54: $XFS_IO_PROG -c "exchangerange -s $(( blksz * (nrblks + 500) )) -d 0 -l $blksz $dir/b" $dir/a`
- `line 57: $XFS_IO_PROG -c "exchangerange -d $(( blksz * (nrblks + 500) )) -s 0 -l $blksz $dir/b" $dir/a`
- `line 60: $XFS_IO_PROG -c "exchangerange -d $(( blksz * (nrblks + 500) )) -s $(( blksz * (nrblks + 500) )) -l $blksz $dir/b" $dir/a`
- `line 63: $XFS_IO_PROG -c "exchangerange -s $(( blksz * (nrblks - 1) )) -d 0 -l $((2 * blksz)) $dir/b" $dir/a`
- `line 66: $XFS_IO_PROG -c "exchangerange -d $(( blksz * (nrblks - 1) )) -s 0 -l $((2 * blksz)) $dir/b" $dir/a`
- `line 69: $XFS_IO_PROG -c "exchangerange -d $(( blksz * (nrblks - 1) )) -s $(( blksz * (nrblks - 1) )) -l $((blksz * 2)) $dir/b" $dir/a`
- `line 74: $XFS_IO_PROG -c "exchangerange -d 0 -s $(( blksz * nrblks )) -l 37 $dir/b" $dir/a`
- `line 77: $XFS_IO_PROG -c "exchangerange -s 0 -d $(( blksz * nrblks )) -l 37 $dir/b" $dir/a`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Extended attributes are part of the persistent state being created, replayed, or verified. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/717.out` (31 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate`, `_require_test`, `_require_scratch`, `_require_chattr i`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 31 line(s); its first visible signals are: 'QA output created by 717; Immutable files; exchangerange: Operation not permitted; Readonly files; exchangerange: Bad file descriptor'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
