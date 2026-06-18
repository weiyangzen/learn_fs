# File Research: sources/os/linux/linux/fs/ntfs/ea.h

## Purpose
Declares NTFS extended attribute, WSL metadata, xattr listing, and optional POSIX ACL interfaces.

## Key Elements
Defines `NTFS_EA_UID`, `NTFS_EA_GID`, and `NTFS_EA_MODE` bit flags used to select which WSL metadata EAs should be written. Exports `ntfs_xattr_handlers`, WSL EA get/set helpers, `ntfs_listxattr()`, and ACL hooks when `CONFIG_NTFS_FS_POSIX_ACL` is enabled.

## Dependencies And Integration
Included by file and inode operation code to bind Linux inode operations to NTFS EA-backed metadata. When POSIX ACL support is disabled, `ntfs_get_acl` and `ntfs_set_acl` are defined as NULL so inode operation tables can be built unconditionally.

## Behavior/Risks
The interface assumes callers hold the appropriate NTFS MFT record mutex around low-level EA updates where needed. `ntfs_ea_set_wsl_inode()` can optionally return the packed EA size for on-disk FILE_NAME metadata updates.
