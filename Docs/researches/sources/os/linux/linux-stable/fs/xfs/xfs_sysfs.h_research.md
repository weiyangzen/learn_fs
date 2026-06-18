# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_sysfs.h

Header for XFS sysfs kobject helpers and exported kobject types.

Key elements:
- Declares kobject types for debug, log, and stats sysfs directories.
- `to_kobj` converts a generic `struct kobject` to embedded `struct xfs_kobj`.
- `xfs_sysfs_release` completes the embedded completion when kobject refcounting releases the object.
- `xfs_sysfs_init` initializes a completion, attaches an optional parent kobject, and calls `kobject_init_and_add`; on failure it drops the kobject reference.
- `xfs_sysfs_del` deletes the kobject, drops its reference, and waits for release completion.
- Declares `xfs_mount_sysfs_init` and `xfs_mount_sysfs_del`.

Research notes:
- Waiting for completion in `xfs_sysfs_del` makes sysfs teardown synchronous from the caller’s point of view.
- All XFS sysfs objects using this helper must embed `struct xfs_kobj`.
