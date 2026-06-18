# sources/test-tools/xfstests/tests/generic/622

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/622`. Test that when the lazytime mount option is enabled, updates to atime, mtime, and ctime are persisted in (at least) the four cases when they should be: - The inode needs to be updated for some change unrelated to file timestamps - Userspace calls fsync(), syncfs(), or sync() - The inode is evicted from memory - More than dirtytime_expire_seconds have elapsed This is in part a regression test for kernel commit 1e249cb5b7fc ("fs: fix lazytime expiration handling in __writeback_single_inode()"). This test failed on XFS without that commit. It is registered with `_begin_fstest auto shutdown metadata atime`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 238 source line(s).
- Harness registration: `_begin_fstest auto shutdown metadata atime`.
- Imported common libraries: `./common/preamble`, `./common/filter`.
- Capability and skip gates: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_xfs_io_command "pwrite"`, `_require_xfs_io_command "fsync"`, `_require_xfs_io_command "syncfs"`.
- Local shell functions: `restore_expiration_settings`, `__expire_inodes`, `expire_inodes`, `expire_timestamps`, `_cleanup`, `get_timestamp`, `do_test`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `DIRTY_EXPIRE_CENTISECS_ORIG=$(</proc/sys/vm/dirty_expire_centisecs)`
- `DIRTY_WRITEBACK_CENTISECS_ORIG=$(</proc/sys/vm/dirty_writeback_centisecs)`
- `DIRTYTIME_EXPIRE_SECONDS_ORIG=$(</proc/sys/vm/dirtytime_expire_seconds)`
- `file=$SCRATCH_MNT/file`
- `expected_time=$(get_timestamp ctime)`

## Control Flow

- Capability gating runs first through `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_xfs_io_command "pwrite"`, `_require_xfs_io_command "fsync"`, plus 1 more.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 28: echo "$DIRTY_EXPIRE_CENTISECS_ORIG" > /proc/sys/vm/dirty_expire_centisecs`
- `line 29: echo "$DIRTY_WRITEBACK_CENTISECS_ORIG" > /proc/sys/vm/dirty_writeback_centisecs`
- `line 30: echo "$DIRTYTIME_EXPIRE_SECONDS_ORIG" > /proc/sys/vm/dirtytime_expire_seconds`
- `line 37: echo 1 > /proc/sys/vm/dirty_expire_centisecs`
- `line 38: echo 1 > /proc/sys/vm/dirty_writeback_centisecs`
- `line 57: echo 1 > /proc/sys/vm/dirtytime_expire_seconds`
- `line 118: echo -e "\n# Testing that lazytime $timestamp_type update is persisted by $persist_method"`
- `line 165: echo "FAIL: $timestamp_type didn't increase after updating it (in-memory)"`
- Key operational lines include:
- `line 80: _require_scratch_shutdown`
- `line 91: _scratch_mkfs &>> $seqres.full`
- `line 92: _scratch_mount`
- `line 96: $XFS_IO_PROG -f $file -c "pwrite 0 100" > /dev/null`
- `line 110: stat -c "%.9${arg}" $file | tr -d '.'`
- `line 127: _scratch_cycle_mount lazytime,strictatime`
- `line 129: _scratch_cycle_mount lazytime`
- `line 154: $XFS_IO_PROG -f $file -c "pwrite 0 100" > /dev/null`
- `line 155: $XFS_IO_PROG -f $file -c "pwrite 0 100" > /dev/null`
- `line 187: $XFS_IO_PROG -r $file -c fsync`
- `line 191: $XFS_IO_PROG $SCRATCH_MNT -c syncfs`
- `line 213: _scratch_shutdown -f`
- `line 217: _scratch_cycle_mount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto shutdown metadata atime`, common helper libraries (`./common/preamble`, `./common/filter`), and the golden-output file `sources/test-tools/xfstests/tests/generic/622.out` (37 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch`, `_require_scratch_shutdown`, `_require_metadata_journaling`, `_require_xfs_io_command "pwrite"`, `_require_xfs_io_command "fsync"`, `_require_xfs_io_command "syncfs"`.

## Risks and Edge Cases

- Failure-injection paths can leave mounts or synthetic device tables behind if cleanup is interrupted.

## Test Signals

The paired `.out` file has 37 line(s); its first visible signals are: 'QA output created by 622; # Testing that lazytime atime update is persisted by other_inode_change; # Testing that lazytime atime update is persisted by sync'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows, post-remount or failure-injection persistence checks. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
