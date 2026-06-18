# sources/test-tools/xfstests/tests/generic/719

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/719`. Test atomic file replacement when (a) the length is the same; (b) the length is different; and (c) someone modifies the original file and we need to cancel the update. The staging file is created empty, which implies that the caller wants a full file replacement. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 104 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_test`.
- Local shell functions: `_cleanup`, `filesnap`, `mkfile`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_test`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 30: echo "$1"`
- `line 56: echo`
- `line 69: echo`
- `line 82: echo`
- `line 100: echo`
- Key operational lines include:
- `line 25: _require_xfs_io_command exchangerange`
- `line 26: _require_xfs_io_command startupdate '-e'`
- `line 31: md5sum $2 | _filter_test_dir`
- `line 49: $XFS_IO_PROG \`
- `line 50: -c 'startupdate -e' \`
- `line 52: -c 'commitupdate -q' \`
- `line 62: $XFS_IO_PROG \`
- `line 63: -c 'startupdate -e' \`
- `line 65: -c 'commitupdate -q' \`
- `line 75: $XFS_IO_PROG \`
- `line 76: -c 'startupdate -e' \`
- `line 78: -c 'commitupdate -q' \`
- `line 89: $XFS_IO_PROG \`
- `line 91: -c 'startupdate -e ' \`
- `line 96: -c 'commitupdate -q' \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/719.out` (40 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_test`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 40 line(s); its first visible signals are: 'QA output created by 719; before commit; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-719/a; wrote 4194304/4194304 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
