# File Research: sources/os/linux/linux/fs/9p/acl.h

## Summary
Declares 9p POSIX ACL interfaces and provides no-op stubs when ACL support is disabled.

## Main Contents
With `CONFIG_9P_FS_POSIX_ACL`, declares ACL get/set, chmod, create, mode, and release helpers. Without it, inode operation hooks are defined as `NULL` and helper functions return success without changing ACL state.

## Important Details
The disabled-ACL stubs let common 9p inode and create paths call ACL helpers unconditionally while compiling out ACL behavior.

## Risks
When ACL support is disabled, create-mode helper `v9fs_acl_mode()` returns 0 without applying any ACL-derived mode changes; callers must rely on non-ACL permission handling.
