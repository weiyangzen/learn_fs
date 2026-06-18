# File Research: sources/os/linux/linux-stable/fs/tracefs/inode.c

Purpose: Implements the tracefs filesystem core: registration, mount options, inode cache, file/directory creation APIs, removal, and permission propagation.

Key responsibilities:
- Maintains tracefs inode slab cache and global inode list for remount updates.
- Implements default tracefs file operations and inode operations for regular files, directories, and tracing instance directories.
- Parses and applies mount options: `uid`, `gid`, and `mode`.
- Reconfigures tracefs on remount and propagates uid/gid changes to tracefs and eventfs inodes.
- Defines superblock, dentry, and fs_context operations.
- Registers the `tracefs` filesystem and creates `/sys/kernel/tracing` mount point.
- Provides exported APIs: `tracefs_create_file()`, `tracefs_create_dir()`, `tracefs_remove()`, and `tracefs_initialized()`.
- Provides `tracefs_create_instance_dir()` for the tracing instances directory with mkdir/rmdir callbacks.

Important interactions:
- Uses simplefs helpers, fs_context parser, security lockdown, sysfs mount-point creation, fsnotify, and eventfs hooks.
- Pins tracefs while creating/removing entries with `simple_pin_fs()` and `simple_release_fs()`.
- Instance directory mkdir/rmdir drops inode locks before calling tracing callbacks.

Notable invariants and risks:
- Tracefs default mode is `0700`.
- Lockdown can prevent creating tracefs/eventfs entries.
- Dentry operations distinguish eventfs dentries by `d_fsdata`; eventfs dentries are kept differently from ordinary tracefs dentries.
- Remount uid/gid updates clear per-inode override flags unless users explicitly changed ownership.
