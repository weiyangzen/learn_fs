# sources/test-tools/xfstests/tests/generic/646

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/646`. Testcase for kernel commit: 50d25484bebe xfs: sync lazy sb accounting on quiesce of read-only mounts After shutdown and readonly mount, a following read-write mount would get wrong number of available blocks. This is caused by unmounting the log on a readonly filesystem doesn't log the sb counters. It is registered with `_begin_fstest auto quick recoveryloop shutdown`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 44 source line(s).
- Harness registration: `_begin_fstest auto quick recoveryloop shutdown`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit xfs 50d25484bebe "xfs: sync lazy sb accounting on quiesce of read-only mounts"`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs 50d25484bebe "xfs: sync lazy sb accounting on quiesce of read-only mounts"`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 28: echo Testing > $SCRATCH_MNT/testfile`
- `line 42: echo "Silence is golden"`
- Key operational lines include:
- `line 21: _require_scratch_shutdown`
- `line 23: _scratch_mkfs > $seqres.full 2>&1`
- `line 25: _scratch_mount`
- `line 31: _scratch_shutdown -f`
- `line 33: _scratch_cycle_mount ro`
- `line 34: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick recoveryloop shutdown`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/646.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs 50d25484bebe "xfs: sync lazy sb accounting on quiesce of read-only mounts"`, `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 646; Silence is golden'. Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
