# File Research: sources/os/linux/linux-stable/fs/sysfs/mount.c

Purpose: Initializes and registers the sysfs filesystem and connects it to kernfs mount infrastructure.

Key responsibilities:
- Creates the global kernfs root and stores `sysfs_root_kn`.
- Defines sysfs fs_context operations and filesystem type.
- Initializes per-mount kernfs context with root, magic number, and network namespace tag.
- Allows user namespace visible sysfs mounts by setting `SB_I_USERNS_VISIBLE` on newly created superblocks.
- Drops namespace references on context free and superblock kill.
- Registers the `sysfs` filesystem at init.

Important interactions:
- Uses kernfs `kernfs_get_tree()`, `kernfs_kill_sb()`, and fs_context support.
- Integrates with kobject namespace helpers for network namespace tagging.
- Adjusts `fc->user_ns` to the owning network namespace user namespace.

Notable invariants and risks:
- Non-kernel mounts require `kobj_ns_current_may_mount(KOBJ_NS_TYPE_NET)`.
- `fc->global = true` forces global superblock namespace behavior while still tagging kernfs entries by namespace.
