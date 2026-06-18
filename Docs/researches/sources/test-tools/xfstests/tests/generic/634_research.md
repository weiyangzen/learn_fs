# sources/test-tools/xfstests/tests/generic/634

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/634`. Make sure we can store and retrieve timestamps on the extremes of the date ranges supported by userspace, and the common places where overflows can happen. This differs from generic/402 in that we don't constrain ourselves to the range that the filesystem claims to support; we attempt various things that /userspace/ can parse, and then check that the vfs clamps and persists the values correctly. NOTE: Old kernels (pre 5.4) allow filesystems to truncate timestamps silently when writing timestamps to disk! This test detects this silent truncation and fails. If you see a failure on such a kernel, contact your distributor for an update. It is registered with `_begin_fstest auto quick atime bigtime`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 106 source line(s).
- Harness registration: `_begin_fstest auto quick atime bigtime`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`.
- Local shell functions: `touchme`, `report`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `test_bigdates=1`
- `test_statx=1`
- `test_statx=0`
- `TZ=UTC stat -c '%y %Y %n' "${file}"`

## Control Flow

- Capability gating runs first through `_require_scratch`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 41: echo "Userspace support of large timestamps: $test_bigdates" >> $seqres.full`
- `line 42: echo "xfs_io support of statx: $test_statx" >> $seqres.full`
- `line 48: echo "$arg" > $SCRATCH_MNT/t_$name`
- `line 55: echo "${file}: $(cat "${file}")"`
- `line 89: echo before >> $seqres.full`
- `line 96: echo after >> $seqres.full`
- `line 104: echo Silence is golden.`
- Key operational lines include:
- `line 28: _scratch_mkfs > $seqres.full`
- `line 29: _scratch_mount`
- `line 37: ($XFS_IO_PROG -c 'help statx' | grep -q 'Print raw statx' && \`
- `line 38: $XFS_IO_PROG -c 'statx -r' $SCRATCH_MNT 2>/dev/null | grep -q 'stat.mtime') || \`
- `line 56: TZ=UTC stat -c '%y %Y %n' "${file}"`
- `line 58: $XFS_IO_PROG -c 'statx -r' "${file}" | grep 'stat.mtime'`
- `line 93: _scratch_cycle_mount`
- `line 101: cmp -s $tmp.before_remount $tmp.after_remount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick atime bigtime`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/634.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 634; Silence is golden.'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
