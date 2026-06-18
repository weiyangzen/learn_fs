# File Research: sources/virtualization/open-iscsi/usr/sysfs.c

Purpose: Provides generic sysfs path resolution, device caching, attribute reads/writes, typed conversion helpers, and `uevent` field extraction. The code is derived from udev sysfs utilities.

Key entry points:
- `sysfs_init()` sets global `sysfs_path` from `SYSFS_PATH` or defaults to `/sys`, then initializes the device cache.
- `sysfs_cleanup()` frees cached `sysfs_device` entries.
- `sysfs_device_get()` resolves supported sysfs device paths, follows symlinks, populates subsystem/driver/kernel names, and caches devices.
- `sysfs_device_get_parent()` and `sysfs_device_get_parent_with_subsystem()` traverse device parents.
- `sysfs_attr_get_value()` reads an attribute or symlink target value from a device path.
- `sysfs_lookup_devpath_by_subsys_id()` maps subsystem/id pairs to sysfs devpaths across `/subsystem`, `/bus`, `/class`, `/module`, `/firmware`, and driver layouts.
- `sysfs_get_value()` composes lookup plus attribute read and filters `<NULL>`/`(null)` values.
- Typed readers: `sysfs_get_uint()`, `sysfs_get_int()`, `sysfs_get_str()`, `sysfs_get_uint64()`, `sysfs_get_uint8()`, and `sysfs_get_uint16()`.
- `sysfs_set_param()` writes a sysfs attribute after path lookup and permission validation.
- `sysfs_get_uevent_field()`, `sysfs_get_uevent_devtype()`, and `sysfs_get_uevent_devname()` read fields from a device `uevent` file.

Implementation notes:
- Device cache entries store devpath, subsystem, driver, kernel name, kernel numeric suffix, and parent pointer.
- `sysfs_resolve_link()` resolves relative symlink targets containing `../` segments into absolute sysfs devpaths relative to `sysfs_path`.
- `sysfs_device_set_values()` also translates `!` in kernel names to `/`, matching sysfs naming behavior.
- `sysfs_attr_get_value()` treats symlink attributes as the final path component of the symlink target, skips directories and unreadable files, reads up to `NAME_SIZE`, and strips trailing newlines.
- Integer readers initialize outputs to `-1`; `sysfs_get_int()` treats `"off"` specially for `iscsi_session` attributes.
- `sysfs_set_param()` requires user-write permission and writes the caller-provided buffer size exactly.
- `sysfs_get_uevent_field()` reads `/uevent` line by line, tokenizes on `=`, and duplicates the requested value.

Dependencies and interactions:
- Uses project list primitives, `strlcpy`/`strlcat` from `sysdeps.h`, and logging.
- Serves higher-level open-iscsi sysfs helpers and mount/session code that need typed reads from kernel sysfs.

Filesystem/storage relevance:
- iSCSI session discovery, mounted-device checks, transport detection, and status reporting all rely on sysfs. This file is the generic sysfs access substrate under those storage-control paths.
