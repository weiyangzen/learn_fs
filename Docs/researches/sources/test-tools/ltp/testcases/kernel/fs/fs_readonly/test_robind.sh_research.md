# sources/test-tools/ltp/testcases/kernel/fs/fs_readonly/test_robind.sh

## Purpose

`test_robind.sh` verifies read-only bind-mount semantics for filesystem test commands. It formats or uses a large test device, mounts it normally, bind-mounts it read-write, bind-mounts it read-only, then expects the supplied command to succeed on the writable views and fail on the read-only view.

## Important APIs, Types, and Functions

Important shell functions are `usage`, `umount_mntpoint`, `cleanup`, `setup`, and `testdir`. It uses legacy LTP `test.sh` helpers such as `tst_require_root`, `tst_tmpdir`, `tst_mkfs`, `tst_brkm`, `tst_resm`, `tst_rmdir`, and `tst_exit`. State is kept in `DIRS`, `device`, `FSTYPES`, `command`, and mount-flag variables for cleanup.

## Control Flow

The script parses `-c`, prepares a temporary directory, chooses filesystem types from arguments or `LTP_BIG_DEV_FS_TYPE`, formats `LTP_BIG_DEV` for non-`ramfs` tests, mounts `dir1`, bind mounts `dir2-bound`, bind mounts `dir3-ro`, remounts the third as `ro,bind`, and calls `testdir` for all three views. `testdir` runs `eval $command`, captures output, and inverts the expected status for the read-only case.

## State and Persistence Behavior

The test creates temporary mountpoints, a `test.log`, and files produced by the command under each mount. `umount_mntpoint` uses mount flags to avoid double unmounts and cleanup removes the temporary LTP directory. The block device contents are overwritten when `tst_mkfs` is called.

## Dependencies and Integration Points

Requires root, `LTP_BIG_DEV` for block filesystems, mount/umount support, filesystem mkfs tools, and the command passed with `-c`. It integrates with LTP through legacy result reporting and cleanup hooks.

## Risks and Edge Cases

`eval $command` is intentionally flexible but shell-sensitive. `getopts c:h:` treats `-h` as if it required an argument. `opts` is not reset per filesystem, so a previous filesystem's mkfs options could leak if an unknown type follows. Failure expectations assume read-only failures return nonzero, which may not hold for read-only-safe commands.

## Test Signals

Passing output is one `TPASS` for each writable normal mount, writable bind mount, and read-only failure case per filesystem. `TBROK` indicates setup or mount failure; `TFAIL` with `test.log` content indicates unexpected command status.
