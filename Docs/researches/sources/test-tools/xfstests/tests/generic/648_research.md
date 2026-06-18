# sources/test-tools/xfstests/tests/generic/648

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/648`. Test nested log recovery with repeated (simulated) disk failures. We kick off fsstress on a loopback filesystem mounted on the scratch fs, then switch out the underlying scratch device with dm-error to see what happens when the disk goes down. Having taken down both fses in this manner, remount them and repeat. This test simulates VM hosts crashing to try to shake out CoW bugs in writeback on the host that cause VM guests to fail to recover. It is registered with `_begin_fstest shutdown auto log metadata eio recoveryloop`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 141 source line(s).
- Harness registration: `_begin_fstest shutdown auto log metadata eio recoveryloop`.
- Imported common libraries: `./common/preamble`, `./common/dmerror`, `./common/reflink`.
- Capability and skip gates: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_loop`, `_require_metadata_journaling $SCRATCH_DEV`.
- Local shell functions: `_cleanup`, `snap_loop_fs`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `scratch_freesp_bytes=$(_get_available_space $SCRATCH_MNT)`
- `loopimg_bytes=$((scratch_freesp_bytes / 3))`
- `loopimg=$SCRATCH_MNT/testfs`
- `loopmnt=$tmp.mount`
- `scratch_aliveflag=$tmp.runsnap`
- `snap_aliveflag=$tmp.snapping`
- `is_unmounted=1`
- `is_unmounted=0`

## Control Flow

- Capability gating runs first through `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_loop`, `_require_metadata_journaling $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 41: echo "Silence is golden."`
- `line 134: echo "final scratch mount failed"`
- Key operational lines include:
- `line 19: _kill_fsstress`
- `line 21: _unmount $loopmnt 2>/dev/null`
- `line 24: _dmerror_unmount`
- `line 25: _dmerror_cleanup`
- `line 36: _require_scratch_reflink`
- `line 37: _require_cp_reflink`
- `line 43: _scratch_mkfs >> $seqres.full 2>&1`
- `line 45: _dmerror_init`
- `line 46: _dmerror_mount`
- `line 54: _mkfs_dev $loopimg`
- `line 64: while [ -e "$scratch_aliveflag" ]; do`
- `line 66: _cp_reflink $loopimg $loopimg.a`
- `line 76: if ! _mount $loopimg $loopmnt -o loop; then`
- `line 83: _run_fsstress_bg -d "$loopmnt" -n 999999 -p "$((LOAD_FACTOR * 4))"`
- `line 95: _dmerror_load_error_table`
- `line 97: _kill_fsstress`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. Shared extent or atomic-update state is exercised, so correctness depends on clone/dedupe/exchange persistence and metadata ordering. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest shutdown auto log metadata eio recoveryloop`, common helper libraries (`./common/preamble`, `./common/dmerror`, `./common/reflink`), and the golden-output file `sources/test-tools/xfstests/tests/generic/648.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_reflink`, `_require_cp_reflink`, `_require_dm_target error`, `_require_loop`, `_require_metadata_journaling $SCRATCH_DEV`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- Shared-extent and exchange operations can expose stale data, permission-bit, or log-ordering bugs that only appear after remount/recovery.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 648; Silence is golden.'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
