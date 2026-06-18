# sources/test-tools/xfstests/tests/generic/640

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/640`. Test that if we fsync a directory A, evict A's inode, move one file from directory A to a directory B, fsync some other inode that is not directory A, B or any inode inside these two directories, and then power fail, the file that was moved is not lost. It is registered with `_begin_fstest auto quick log`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 99 source line(s).
- Harness registration: `_begin_fstest auto quick log`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`.
- Capability and skip gates: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `foo_in_a=0`
- `foo_in_b=0`
- `foo_in_a=1`
- `foo_in_b=1`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 38: echo -n "hello world" > $SCRATCH_MNT/A/foo`
- `line 50: echo 2 > /proc/sys/vm/drop_caches`
- `line 78: echo "File foo data: $(cat $SCRATCH_MNT/A/foo)"`
- `line 83: echo "File foo data: $(cat $SCRATCH_MNT/B/foo)"`
- `line 88: echo "File foo found in A/ and B/"`
- `line 90: echo "File foo is missing"`
- Key operational lines include:
- `line 18: _cleanup_flakey`
- `line 30: _scratch_mkfs >>$seqres.full 2>&1`
- `line 32: _init_flakey`
- `line 33: _scratch_mount`
- `line 41: _scratch_sync`
- `line 45: $XFS_IO_PROG -c "fsync" $SCRATCH_MNT/A`
- `line 58: $XFS_IO_PROG -c "fsync" $SCRATCH_MNT/baz`
- `line 61: _flakey_drop_and_remount`
- `line 97: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick log`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`), and the golden-output file `sources/test-tools/xfstests/tests/generic/640.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_dm_target flakey`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 640; File foo data: hello world'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
