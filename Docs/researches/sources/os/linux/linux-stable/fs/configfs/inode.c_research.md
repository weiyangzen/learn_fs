# File Research: sources/os/linux/linux-stable/fs/configfs/inode.c

This file implements configfs inode creation, persistent attribute metadata, and dentry dropping helpers.

Key responsibilities:
- Implements `configfs_setattr()` to apply VFS setattr and persist non-default mode/uid/gid/timestamps in the dirent.
- Creates new configfs inodes with `configfs_new_inode()`.
- Creates uninstantiated dentry inodes with `configfs_create()`.
- Provides `configfs_get_name()` for dirents.
- Provides `configfs_drop_dentry()` to unhash and unlink attribute dentries.

Important control flow:
- First setattr allocates `sd->s_iattr` with default metadata, then records changed fields after `simple_setattr()` succeeds.
- `configfs_new_inode()` uses `ram_aops`, generic configfs inode operations, and either persistent `s_iattr` or default attributes.
- `configfs_create()` rejects null or already-positive dentries, allocates an inode, updates parent timestamps, and assigns lockdep class for default groups when configured.
- `configfs_drop_dentry()` handles positive dentries under dentry lock and performs `__simple_unlink()` from the parent.

Dependencies:
- Used by directory, file, mount, and symlink implementations.
- Lockdep class depth is supplied by `dir.c`.

Risks and invariants:
- Configfs persists chmod/chown/timestamp changes in dirents, not in backing storage.
- Setgid stripping follows normal capability/group checks.
- `configfs_get_name()` depends on dirent type: directories and links use dentry names; attributes use `ca_name`.
