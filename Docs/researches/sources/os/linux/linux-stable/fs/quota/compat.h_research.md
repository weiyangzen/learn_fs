# File Research: sources/os/linux/linux-stable/fs/quota/compat.h

## Summary
Defines 32-bit compatibility structures used by quota ioctl/syscall handling.

## Main Responsibilities
- Define `compat_if_dqblk` for compatible quota block/inode limit and usage fields.
- Define `compat_fs_qfilestat` for compatible quota file statistics.
- Define `compat_fs_quota_stat` for compatible filesystem quota status.

## Important Behavior
The structures use `compat_u64`, `compat_uint_t`, and `compat_int_t` so 32-bit userspace layouts are stable when handled by a 64-bit kernel.

## Cross-File Interactions
Included by quota syscall/compat handling code outside this group to translate quota status and limit structures between native and compat ABIs.
