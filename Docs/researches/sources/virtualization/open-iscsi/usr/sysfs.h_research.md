# File Research: sources/virtualization/open-iscsi/usr/sysfs.h

Purpose: Declares the generic sysfs utility API and cached device representation used by open-iscsi.

Key definitions:
- `PATH_SIZE` is 512 and `NAME_SIZE` is 256 for sysfs path/name buffers.
- `struct sysfs_device` stores list linkage, cached parent pointer, devpath, subsystem, kernel name, kernel numeric suffix, and driver name.
- `sysfs_path` is the global base path, normally `/sys`.

Declared APIs:
- Initialization/cleanup: `sysfs_init()`, `sysfs_cleanup()`.
- Device helpers: `sysfs_device_set_values()`, `sysfs_device_get()`, `sysfs_device_get_parent()`, `sysfs_device_get_parent_with_subsystem()`.
- Path/value helpers: `sysfs_attr_get_value()`, `sysfs_resolve_link()`, `sysfs_lookup_devpath_by_subsys_id()`, `sysfs_get_value()`.
- Typed readers/writer: `sysfs_get_uint()`, `sysfs_get_int()`, `sysfs_get_str()`, `sysfs_get_uint64()`, `sysfs_get_uint8()`, `sysfs_get_uint16()`, `sysfs_set_param()`.
- Uevent helpers: `sysfs_get_uevent_field()`, `sysfs_get_uevent_devtype()`, and `sysfs_get_uevent_devname()`.

Dependencies and interactions:
- Includes `stdint.h`, project `list.h`, and project string helpers.

Filesystem/storage relevance:
- Exposes reusable sysfs primitives that the iSCSI userspace tools use to map sessions, hosts, SCSI devices, and block devices into kernel-visible storage state.
