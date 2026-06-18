# File Research: sources/os/linux/linux-stable/fs/jffs2/acl.h

## Scope
Declares JFFS2 on-medium ACL structures and POSIX ACL function prototypes/stubs.

## Contents
Defines `jffs2_acl_entry`, `jffs2_acl_entry_short`, and `jffs2_acl_header`. The header uses JFFS2 integer types and a flexible `a_entries[]` payload.

When `CONFIG_JFFS2_FS_POSIX_ACL` is enabled, declares `jffs2_get_acl()`, `jffs2_set_acl()`, `jffs2_init_acl_pre()`, and `jffs2_init_acl_post()`. Otherwise, maps ACL hooks to `NULL` or no-op success stubs.

## Dependencies
Relies on POSIX ACL types, inode/dentry declarations from including context, and JFFS2 endian integer typedefs.

## Risks And Invariants
The disabled-config stubs allow callers to avoid preprocessor branching. Structure layout must match `acl.c` serialization and existing on-flash ACL data.
