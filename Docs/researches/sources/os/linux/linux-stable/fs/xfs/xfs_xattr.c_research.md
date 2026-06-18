# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_xattr.c

## Purpose

Provides XFS VFS extended attribute integration. It maps Linux xattr namespaces to XFS attribute operations and implements listxattr formatting.

## Main Responsibilities

- Enables log-assisted xattrs for debug/LARP configurations when supported.
- Performs xattr set/create/replace/remove through `xfs_attr_change`.
- Attaches quotas before attribute updates.
- Provides user, trusted, and security xattr handlers.
- Converts VFS xattr flags into XFS attribute update operations.
- Lists xattrs with namespace prefixes.
- Hides private namespaces and gates trusted entries behind `CAP_SYS_ADMIN`.
- Translates legacy ACL xattr names to system POSIX ACL names.

## Important Invariants

- Shutdown filesystems reject xattr changes with `-EIO`.
- Attribute fork zap state rejects get/list operations.
- Root/security namespaces may use reserved blocks to avoid ENOSPC failures for critical metadata.
- Logged xattrs require a compatible filesystem feature set.
- `listxattr` returns `-ERANGE` if the caller buffer is too small.

## Dependencies

Uses XFS attr/libxfs code, DA args, quota attach, ACL helpers, VFS xattr handlers, and incompat log feature management.

## Research Notes

This is mostly an adapter layer. The high-risk behavior is enabling logged xattrs and correctly translating namespace exposure and ACL names.
