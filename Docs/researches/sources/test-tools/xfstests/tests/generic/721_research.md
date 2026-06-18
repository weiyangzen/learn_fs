# sources/test-tools/xfstests/tests/generic/721

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/721`. Test non-root atomic file updates when (a) the file contents are cloned into the staging file; and (b) when the staging file is created empty. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 125 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/reflink`.
- Capability and skip gates: `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`, `_require_user`.
- Local shell functions: `_cleanup`, `filesnap`, `mkfile`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `dir=$TEST_DIR/test-$seq`
- `blksz=65536`
- `nrblks=64`
- `cmd="$XFS_IO_PROG \`
- `cmd="$XFS_IO_PROG \`
- `cmd="$XFS_IO_PROG \`
- `cmd="$XFS_IO_PROG \`
- `cmd="$XFS_IO_PROG \`

## Control Flow

- Capability gating runs first through `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`, `_require_user`.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 30: echo "$1"`
- `line 58: echo`
- `line 73: echo`
- `line 87: echo`
- `line 102: echo`
- `line 121: echo`
- Key operational lines include:
- `line 24: _require_xfs_io_command startupdate`
- `line 25: _require_test_reflink`
- `line 31: md5sum $2 | _filter_test_dir`
- `line 50: cmd="$XFS_IO_PROG \`
- `line 51: -c 'startupdate' \`
- `line 53: -c 'commitupdate -q' \`
- `line 64: cmd="$XFS_IO_PROG \`
- `line 65: -c 'startupdate' \`
- `line 68: -c 'commitupdate -q' \`
- `line 79: cmd="$XFS_IO_PROG \`
- `line 80: -c 'startupdate' \`
- `line 82: -c 'commitupdate -q' \`
- `line 94: cmd="$XFS_IO_PROG \`
- `line 95: -c 'startupdate' \`
- `line 97: -c 'cancelupdate' \`
- `line 109: cmd="$XFS_IO_PROG \`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/721.out` (48 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command startupdate`, `_require_test_reflink`, `_require_test`, `_require_user`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 48 line(s); its first visible signals are: 'QA output created by 721; before commit; d712f003e9d467e063cda1baf319b928  TEST_DIR/test-721/a; wrote 56320/56320 bytes at offset 45056; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
