# sources/test-tools/xfstests/tests/generic/725

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/725`. Test scatter-gather atomic file commits. Use the startupdate command to create a temporary file, write sparsely to it, then commitupdate -h to perform the scattered update. It is registered with `_begin_fstest auto quick fiexchange`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 55 source line(s).
- Harness registration: `_begin_fstest auto quick fiexchange`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 38: echo commit | tee -a $seqres.full`
- Key operational lines include:
- `line 24: _require_xfs_io_command exchangerange`
- `line 25: _require_xfs_io_command startupdate '-e'`
- `line 28: _scratch_mkfs >> $seqres.full`
- `line 29: _scratch_mount`
- `line 34: _scratch_sync`
- `line 35: md5sum $SCRATCH_MNT/a | _filter_scratch`
- `line 39: $XFS_IO_PROG \`
- `line 41: -c 'startupdate -e' \`
- `line 46: -c 'commitupdate -h -k' \`
- `line 49: _scratch_cycle_mount`
- `line 51: md5sum $SCRATCH_MNT/a | _filter_scratch`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick fiexchange`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/725.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_xfs_io_command exchangerange`, `_require_xfs_io_command startupdate '-e'`, `_require_scratch`, `_require_congruent_file_oplen $SCRATCH_MNT 65536`.

## Risks and Edge Cases

- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 725; 310f146ce52077fcd3308dcbe7632bb2  SCRATCH_MNT/a; commit; e9cbfe8489a68efaa5fcf40cf3106118  SCRATCH_MNT/a'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
