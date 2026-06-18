# sources/test-tools/xfstests/tests/generic/741

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/741`. Attempt to mount both the DM physical device and the DM flakey device. Verify the returned error message. It is registered with `_begin_fstest auto quick volume tempfsid`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 62 source line(s).
- Harness registration: `_begin_fstest auto quick volume tempfsid`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmflakey`.
- Capability and skip gates: `_require_test`, `_require_scratch`, `_require_dm_target flakey`, `_fixed_by_fs_commit btrfs 2f1aeab9fca1 "btrfs: return accurate error code on open failure"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `extra_mnt=$TEST_DIR/extra_mnt`

## Control Flow

- Capability gating runs first through `_require_test`, `_require_scratch`, `_require_dm_target flakey`, `_fixed_by_fs_commit btrfs 2f1aeab9fca1 "btrfs: return accurate error code on open failure"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- Key operational lines include:
- `line 19: _unmount $extra_mnt &> /dev/null`
- `line 20: _unmount $extra_mnt &> /dev/null`
- `line 22: _scratch_unmount`
- `line 23: _cleanup_flakey`
- `line 39: _scratch_mkfs >> $seqres.full`
- `line 40: _init_flakey`
- `line 41: _scratch_mount`
- `line 49: _mount $NON_FLAKEY_DEV $extra_mnt 2>/dev/null && \`
- `line 53: _scratch_unmount`
- `line 54: _mount $NON_FLAKEY_DEV $extra_mnt 2>/dev/null && \`
- `line 58: _cleanup_flakey`
- `line 59: _scratch_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick volume tempfsid`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmflakey`), and the golden-output file `sources/test-tools/xfstests/tests/generic/741.out` (1 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_test`, `_require_scratch`, `_require_dm_target flakey`, `_fixed_by_fs_commit btrfs 2f1aeab9fca1 "btrfs: return accurate error code on open failure"`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 1 line(s); its first visible signals are: 'QA output created by 741'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
