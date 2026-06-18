# File Research: sources/os/linux/linux-stable/fs/efivarfs/inode.c

## Summary
Implements efivarfs inode creation, directory operations, immutable flag handling, and custom setattr behavior.

## Main Responsibilities
- Allocates inodes with mount uid/gid.
- Validates efivarfs filenames of `Name-GUID` form.
- Creates new variable dentries.
- Deletes firmware variables on unlink.
- Exposes and updates `FS_IMMUTABLE_FL`.

## Key APIs
- `efivarfs_get_inode()`
- `efivarfs_dir_inode_operations`

## Important Behavior
Created variables copy the filename prefix into UTF-16-ish firmware-name storage and parse the trailing GUID. The Linux EFI random seed variable is blocked from creation. Variables not whitelisted by validation policy are created immutable by default.

## Risks
Name validation is security-sensitive because filenames encode firmware variable identity. `efivarfs_setattr()` intentionally avoids normal size updates so file size continues to reflect firmware variable state.
