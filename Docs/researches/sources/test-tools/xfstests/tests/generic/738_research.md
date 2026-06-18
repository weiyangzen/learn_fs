# sources/test-tools/xfstests/tests/generic/738

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/738`. Test possible deadlock of umount and reclaim memory when there are EOF blocks in files. It is registered with `_begin_fstest auto quick freeze`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 54 source line(s).
- Harness registration: `_begin_fstest auto quick freeze`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit xfs ab23a7768739 "xfs: per-cpu deferred inode inactivation queues"`, `_require_scratch`, `_require_freeze`.
- Local shell functions: `_cleanup`, `create_eof_block_file`.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs ab23a7768739 "xfs: per-cpu deferred inode inactivation queues"`, `_require_scratch`, `_require_freeze`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- User-visible phase markers include:
- `line 46: echo 3 > /proc/sys/vm/drop_caches &`
- `line 52: echo "Silence is golden"`
- Key operational lines include:
- `line 26: _scratch_mkfs >> $seqres.full`
- `line 27: _scratch_mount`
- `line 37: $XFS_IO_PROG -fc "pwrite 0 64k" $SCRATCH_MNT/testfile >> $seqres.full`
- `line 42: _scratch_sync`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick freeze`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/738.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs ab23a7768739 "xfs: per-cpu deferred inode inactivation queues"`, `_require_scratch`, `_require_freeze`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 738; Silence is golden'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
