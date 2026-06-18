# sources/test-tools/xfstests/tests/generic/691

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/691`. Make sure filesystem quota works well, after soft limits are exceeded. The fs quota should allow more space allocation before exceeding hard limits and with in grace time. But different with other similar testing, this case tries to write many small files, to cover bc37e4fb5cac (xfs: revert "xfs: actually bump warning counts when we send warnings"). If there's a behavior change some day, this case might help to detect that too. It is registered with `_begin_fstest auto quota`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 109 source line(s).
- Harness registration: `_begin_fstest auto quota`.
- Imported common libraries: `./common/preamble`, `./common/quota`.
- Capability and skip gates: `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_prjquota $SCRATCH_DEV`.
- Local shell functions: `_cleanup`, `filter_quota`, `exercise`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `projid=$seq`
- `file=$SCRATCH_MNT/t/testfile`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_prjquota $SCRATCH_DEV`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- User-visible phase markers include:
- `line 63: echo "= Test type=$type quota =" >>$seqres.full`
- `line 86: echo "Unexpected error (type=$type)!"`
- Key operational lines include:
- `line 38: _scratch_mkfs >$seqres.full 2>&1`
- `line 39: _scratch_enable_pquota`
- `line 64: _scratch_unmount`
- `line 65: _scratch_mkfs >>$seqres.full 2>&1`
- `line 67: _scratch_enable_pquota`
- `line 80: _su $qa_user -c "$XFS_IO_PROG -f -t -c 'pwrite 0 2m' -c fsync ${file}.0" >>$seqres.full`
- `line 84: _su "$qa_user" -c "$XFS_IO_PROG -f -c 'pwrite 0 1m' -c fsync ${file}.$i" >>$seqres.full`
- `line 94: _su $qa_user -c "$XFS_IO_PROG -f -t -c 'pwrite 0 100m' -c fsync ${file}.hard.0" 2>&1 >/dev/null | filter_quota $type`
- `line 96: _su "$qa_user" -c "$XFS_IO_PROG -f -c 'pwrite 0 1m' -c fsync ${file}.hard.$i" 2>&1 | filter_quota $type`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quota`, common helper libraries (`./common/preamble`, `./common/quota`), and the golden-output file `sources/test-tools/xfstests/tests/generic/691.out` (34 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_quota`, `_require_user`, `_require_group`, `_require_prjquota $SCRATCH_DEV`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 34 line(s); its first visible signals are: 'QA output created by 691; Error: Disk quota exceeded; Error: Disk quota exceeded; Error: Disk quota exceeded; Error: Disk quota exceeded'. Runtime pass/fail is primarily the command exit status plus golden-output comparison. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
