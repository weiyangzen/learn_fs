# File Research: sources/os/linux/linux-stable/fs/ufs/Kconfig

## Summary
Defines Linux kernel configuration options for UFS filesystem support.

## Main Responsibilities
- Enables `CONFIG_UFS_FS` as a block filesystem using buffer heads.
- Documents read-only support for BSD/System V style UFS variants and UFS2.
- Provides optional dangerous experimental write support through `CONFIG_UFS_FS_WRITE`.
- Provides optional verbose debug logging through `CONFIG_UFS_DEBUG`.

## Important Behavior
The main prompt labels UFS support as read-only, while write support is a separate explicit dangerous option.

## Risks
Enabling write support exposes experimental code paths in allocation, truncation, inode update, directory mutation, and superblock accounting.
