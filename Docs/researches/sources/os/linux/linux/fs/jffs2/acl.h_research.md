# File Research: sources/os/linux/linux/fs/jffs2/acl.h

## Role

`acl.h` declares the JFFS2 on-flash ACL structures and exposes ACL helper prototypes or no-op definitions depending on `CONFIG_JFFS2_FS_POSIX_ACL`.

## Structures

- `struct jffs2_acl_entry`: full ACL entry with tag, permissions, and id.
- `struct jffs2_acl_entry_short`: compact ACL entry with tag and permissions only.
- `struct jffs2_acl_header`: ACL version plus flexible array of full entries.

The implementation in `acl.c` stores the first four base ACL entry types as short entries and named user/group entries as full entries.

## Conditional API

When POSIX ACL support is enabled, the header declares:
- `jffs2_get_acl()`
- `jffs2_set_acl()`
- `jffs2_init_acl_pre()`
- `jffs2_init_acl_post()`

When disabled:
- `jffs2_get_acl` and `jffs2_set_acl` are defined as `NULL`.
- ACL initialization helpers become no-op macros returning success.

## Integration

The header is included by JFFS2 code that needs ACL hooks without requiring the ACL implementation to be present in all builds. It lets inode and VFS operation setup compile cleanly with or without POSIX ACL support.

## Important Invariants

- Structure field types use JFFS2 endian-aware integer aliases (`jint16_t`, `jint32_t`).
- Callers must tolerate ACL hooks being `NULL` when the feature is disabled.
- The serialized layout must stay compatible with `acl.c` parsing and writing.

## Research Notes

This file is primarily an ABI/layout definition for JFFS2 ACL xattrs plus a build-time compatibility shim.
