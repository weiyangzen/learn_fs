# sources/test-tools/xfstests/tests/generic/743

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/743`. This is a regression test for a kernel hang that I saw when creating a memory mapping, injecting EIO errors on the block device, and invoking MADV_POPULATE_READ on the mapping to fault in the pages. It is registered with `_begin_fstest auto rw eio mmap`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 65 source line(s).
- Harness registration: `_begin_fstest auto rw eio mmap`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/dmerror`.
- Capability and skip gates: `_fixed_by_kernel_commit 631426ba1d45 "mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly"`, `_require_xfs_io_command madvise -R`, `_require_scratch`, `_require_dm_target error`, `_require_command "$TIMEOUT_PROG" "timeout"`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `filesz=2m`

## Control Flow

- Capability gating runs first through `_fixed_by_kernel_commit 631426ba1d45 "mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly"`, `_require_xfs_io_command madvise -R`, `_require_scratch`, `_require_dm_target error`, `_require_command "$TIMEOUT_PROG" "timeout"`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 49: echo read with no errors`
- `line 57: echo read with IO errors`
- Key operational lines include:
- `line 12: _begin_fstest auto rw eio mmap`
- `line 19: _dmerror_unmount`
- `line 20: _dmerror_cleanup`
- `line 28: "mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly"`
- `line 32: _require_xfs_io_command madvise -R`
- `line 35: _require_command "$TIMEOUT_PROG" "timeout"`
- `line 37: _scratch_mkfs >> $seqres.full 2>&1`
- `line 38: _dmerror_init`
- `line 43: _dmerror_mount`
- `line 44: $XFS_IO_PROG -f -c "pwrite -S 0x58 0 $filesz" "$SCRATCH_MNT/a" >> $seqres.full`
- `line 45: _dmerror_unmount`
- `line 46: _dmerror_mount`
- `line 50: $TIMEOUT_PROG -s KILL 10s $XFS_IO_PROG -c "mmap -r 0 $filesz" -c "madvise -R 0 $filesz" "$SCRATCH_MNT/a"`
- `line 51: _dmerror_unmount`
- `line 52: _dmerror_mount`
- `line 56: stat "$SCRATCH_MNT/a" >> $seqres.full`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Synthetic block-device state can be introduced through device-mapper, loop, SCSI debug, or huge-device helpers and must be cleaned even on failure. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto rw eio mmap`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/dmerror`), and the golden-output file `sources/test-tools/xfstests/tests/generic/743.out` (4 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_kernel_commit 631426ba1d45 "mm/madvise: make MADV_POPULATE_(READ|WRITE) handle VM_FAULT_RETRY properly"`, `_require_xfs_io_command madvise -R`, `_require_scratch`, `_require_dm_target error`, `_require_command "$TIMEOUT_PROG" "timeout"`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.
- mmap/page-fault regressions are often race-prone and may manifest as hangs rather than clean command failures.

## Test Signals

The paired `.out` file has 4 line(s); its first visible signals are: 'QA output created by 743; read with no errors; read with IO errors; madvise: Bad address'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, xfstests output filters, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
