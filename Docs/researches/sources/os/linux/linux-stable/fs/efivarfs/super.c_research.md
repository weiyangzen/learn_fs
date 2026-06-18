# File Research: sources/os/linux/linux-stable/fs/efivarfs/super.c

## Summary
Implements efivarfs mount, superblock, dentry, statfs, freeze/thaw resync, and module registration logic.

## Main Responsibilities
- Allocates efivarfs private inodes.
- Parses `uid=` and `gid=` mount options.
- Builds the root and populates variable dentries from firmware.
- Handles case-sensitive variable names and case-insensitive GUID suffixes.
- Tracks EFI ops read-only/read-write notifier events.
- Resyncs filesystem state on thaw.

## Key APIs
- `efivarfs_variable_is_present()`
- `efivarfs_init_fs_context()`
- `efivarfs_kill_sb()`

## Important Behavior
Mount uses `get_tree_single()`. Initial population calls `efivar_init()` and creates persistent dentries for each firmware variable except the Linux EFI random seed. `statfs()` reports exact EFI storage information when firmware supports `QueryVariableInfo()`.

## Risks
Dentry hashing/comparison must match firmware identity rules. Thaw resync deletes missing variables and creates newly discovered ones, so it mutates the dentry tree based on firmware state.
