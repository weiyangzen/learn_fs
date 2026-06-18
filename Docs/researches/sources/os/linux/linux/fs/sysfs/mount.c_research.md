# File Research: sources/os/linux/linux/fs/sysfs/mount.c

Purpose: sysfs filesystem registration, fs_context setup, kernfs root creation, namespace handling, and superblock teardown.

Key structures and APIs:
- Maintains `sysfs_root` and exported internal `sysfs_root_kn`.
- `sysfs_init_fs_context()` allocates kernfs fs context, checks namespace mount permission, grabs current network namespace tag, sets magic `SYSFS_MAGIC`, and marks context global.
- `sysfs_fs_context_free()` drops namespace tag and frees kernfs context.
- `sysfs_kill_sb()` kills kernfs superblock and drops namespace tag.
- `sysfs_init()` creates the kernfs root and registers `sysfs_fs_type`.

Namespace/security notes:
- Non-kernel mounts require `kobj_ns_current_may_mount(KOBJ_NS_TYPE_NET)`.
- If a net namespace tag exists, `fc->user_ns` is switched to that namespace’s user namespace.
- Filesystem type uses `FS_USERNS_MOUNT | FS_USERNS_MOUNT_RESTRICTED`.
