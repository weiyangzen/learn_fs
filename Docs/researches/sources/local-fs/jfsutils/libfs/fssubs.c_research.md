# File Research: sources/local-fs/jfsutils/libfs/fssubs.c

## Purpose
Provides platform-dependent filesystem/device checks used before running JFS tools: root read-only detection, mounted-device detection, and fstab/type validation.

## Main Functions
- `Is_Root_Mounted_RO()`: attempts to create `/.ismount-test-file`; returns `MSG_JFS_VOLUME_IS_MOUNTED_RO` on `EROFS`, otherwise 0.
- `Is_Device_Mounted(char *Device_Name)`: implemented either via `mntent` (`/proc/mounts`, then `MOUNTED`) or via BSD-style `getmntinfo()`.
- `Is_Device_Type_JFS(char *Device_Name)`: checks `/etc/fstab`/mount metadata for JFS type, depending on platform support.

## Linux/mntent Path
- Reads `/proc/mounts`, falling back to `MOUNTED`.
- Matches `Device_Name` against `mnt_fsname`.
- Special-cases root because mount tables may list `/dev/root`; compares `stat("/")` device with candidate device `st_rdev`.
- Distinguishes mounted JFS, mounted read-only JFS, mounted non-JFS, missing fstab entry, and mount-list access errors.

## BSD/getmntinfo Path
- Normalizes `/dev/` prefixes and raw-device naming.
- Uses `f_fstypename == "jfs"` for type checks.
- Notes read-only detection as unimplemented in this path.

## Dependencies
Uses `devices.h` and `message.h` for return codes and device helpers; build-time feature macros select mount APIs.

## Notes
The root read-only probe writes to `/`, so callers should expect side effects when permissions allow creation/unlink of the test file.
