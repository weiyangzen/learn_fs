# File Research: sources/os/linux/linux-stable/fs/efivarfs/internal.h

## Summary
Defines efivarfs private structures and cross-file interfaces.

## Main Contents
- `struct efivarfs_mount_opts`
- `struct efivarfs_fs_info`
- `struct efi_variable`
- `struct efivar_entry`
- Firmware variable helper declarations.
- File, directory, and inode operation declarations.

## Important Details
`efivar_entry` embeds both firmware identity and VFS inode state, plus `open_count` and `removed` state for deferred deletion. The helper `efivar_entry()` converts a VFS inode to its containing entry.

## Risks
The header encodes the central lifetime model: firmware variables, dentries, and inodes are represented by one embedded object.
