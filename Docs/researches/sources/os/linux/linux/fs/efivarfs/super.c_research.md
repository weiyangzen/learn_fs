# File Research: sources/os/linux/linux/fs/efivarfs/super.c

Implements efivarfs mounting, superblock operations, dentry handling, enumeration, freeze/thaw resync, and module registration.

Key behavior:
- Allocates/free `struct efivar_entry` inodes.
- Registers a notifier so EFI variable ops transitions can force the superblock read-only or read-write.
- `statfs` reports firmware variable storage via `QueryVariableInfo()` when available and accounts for reserved space.
- Custom dentry compare/hash treats the variable-name portion as case-sensitive and the GUID portion as case-insensitive.
- Mount options support `uid=` and `gid=`.
- `fill_super` sets magic, operations, dentry ops, no-cache dentries, root inode, write support flags, notifier, and initial EFI variable enumeration.
- Enumeration callback skips the Linux EFI random seed variable and creates a persistent dentry per firmware variable.
- `unfreeze_fs` rescans firmware variables, updates inode sizes, removes missing variables, and creates newly discovered entries.
- `init_fs_context` rejects unavailable EFI services and initializes default root uid/gid.
- Registers the `efivarfs` filesystem with `FS_POWER_FREEZE`.

Important interactions:
- Uses `efivar_init()` from `vars.c` for enumeration and duplicate detection.
- Uses `try_lookup_noperm()` for variable presence and resync checks.
- Backed by anonymous/single-super style VFS state, not a block device.
