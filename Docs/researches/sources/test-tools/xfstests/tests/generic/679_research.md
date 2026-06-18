# sources/test-tools/xfstests/tests/generic/679

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/679`. Test that if we call fallocate against a file range that has a mix of holes and written extents, the fallocate succeeds if the filesystem has enough free space to allocate extents for the holes. It is registered with `_begin_fstest auto quick prealloc fiemap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 60 source line(s).
- Harness registration: `_begin_fstest auto quick prealloc fiemap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/punch`.
- Capability and skip gates: `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_exclude_fs xfs`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_exclude_fs xfs`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 50: echo -n "Number of unwritten extents in the file: "`
- `line 55: echo "File content after fallocate:"`
- Key operational lines include:
- `line 19: _require_xfs_io_command "falloc"`
- `line 31: _scratch_mkfs_sized $((1024 * 1024 * 1024)) >>$seqres.full 2>&1`
- `line 32: _scratch_mount`
- `line 36: $XFS_IO_PROG -f -c "pwrite -S 0xab 0 200M" \`
- `line 44: $XFS_IO_PROG -c "falloc 0 600M" $SCRATCH_MNT/foobar`
- `line 48: _scratch_cycle_mount`
- `line 51: $XFS_IO_PROG -c "fiemap -v" $SCRATCH_MNT/foobar | _filter_fiemap | \`
- `line 55: echo "File content after fallocate:"`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick prealloc fiemap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/punch`), and the golden-output file `sources/test-tools/xfstests/tests/generic/679.out` (20 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_xfs_io_command "falloc"`, `_require_xfs_io_command "fiemap"`, `_exclude_fs xfs`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 20 line(s); its first visible signals are: 'QA output created by 679; wrote 209715200/209715200 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 209715200/209715200 bytes at offset 210763776; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec)'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
