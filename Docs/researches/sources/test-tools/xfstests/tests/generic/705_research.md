# sources/test-tools/xfstests/tests/generic/705

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/705`. Test an issue in the truncate codepath where on-disk inode sizes are logged prematurely via the free eofblocks path on file close. It is registered with `_begin_fstest auto shutdown`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 44 source line(s).
- Harness registration: `_begin_fstest auto shutdown`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_command "$FILEFRAG_PROG" filefrag`.
- Local shell functions: none visible.
- External `$here/src` helpers: none visible.

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_command "$FILEFRAG_PROG" filefrag`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 20: echo "Create many small files with one extent at least"`
- `line 25: echo "Shutdown the fs suddently"`
- `line 28: echo "Cycle mount"`
- `line 31: echo "Check file's (di_size > 0) extents"`
- `line 36: echo " - $f get no extents, but its di_size > 0"`
- Key operational lines include:
- `line 14: _require_scratch_shutdown`
- `line 17: _scratch_mkfs > $seqres.full 2>&1`
- `line 18: _scratch_mount`
- `line 22: $XFS_IO_PROG -f -c "pwrite 0 4k" $SCRATCH_MNT/file.$i >/dev/null 2>&1`
- `line 26: _scratch_shutdown`
- `line 29: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Cleanup relies mostly on the default xfstests harness cleanup plus explicit unmounts/removals in the script body.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto shutdown`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/705.out` (5 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_command "$FILEFRAG_PROG" filefrag`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 5 line(s); its first visible signals are: "QA output created by 705; Create many small files with one extent at least; Shutdown the fs suddently; Cycle mount; Check file's (di_size > 0) extents". Runtime pass/fail is also signaled by post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
