# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/volrefcnt.c

## Role
Regression test for UBI volume sysfs reference counting during volume deletion.

## Main Behavior
- Creates a small dynamic volume.
- Opens `/sys/class/ubi/ubiX_Y/usable_eb_size`.
- Removes the volume while the sysfs file remains open.
- Confirms reading from the stale fd fails.
- Closes the fd and confirms the sysfs file cannot be opened again.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_dev_info`.
- Uses direct sysfs path format `SYSFS_FILE`.

## Notes
- `PROGRAM_NAME` is `"rmvol"`, not `volrefcnt`.
- Tests kernel lifetime/reference cleanup, not volume I/O.
