# File Research: sources/os/linux/linux-stable/fs/jffs2/acl.c

## Scope
Implements JFFS2 POSIX ACL serialization/deserialization and VFS ACL get/set/init hooks backed by JFFS2 xattrs.

## Primary APIs
Provides `jffs2_get_acl()`, `jffs2_set_acl()`, `jffs2_init_acl_pre()`, and `jffs2_init_acl_post()`. Internal helpers are `jffs2_acl_size()`, `jffs2_acl_count()`, `jffs2_acl_from_medium()`, `jffs2_acl_to_medium()`, and `__jffs2_set_acl()`.

## Behavior
On-medium ACL format stores a versioned header and entries. The first four ACL entries use a short format without IDs when possible; named user/group entries use the full format with UID/GID.

`jffs2_get_acl()` maps access/default ACL type to a JFFS2 xattr prefix, reads xattr length, allocates a buffer, fetches xattr data, converts it to `struct posix_acl`, and returns `NULL` for missing or unsupported xattr storage.

`jffs2_set_acl()` validates type, updates inode mode for access ACLs via `posix_acl_update_mode()`, writes mode changes through `jffs2_do_setattr()`, rejects default ACLs on non-directories, serializes ACLs into xattrs, and updates the inode ACL cache.

`jffs2_init_acl_pre()` computes inherited ACLs before inode creation, caches them on the inode, and updates the mode. `jffs2_init_acl_post()` writes cached default/access ACL xattrs after inode creation.

## State And Data
Uses `struct jffs2_acl_header`, `jffs2_acl_entry_short`, and `jffs2_acl_entry`, with JFFS2 endian conversion helpers and init-user-namespace UID/GID conversion.

## Dependencies
Depends on POSIX ACL core, JFFS2 xattr get/set routines, JFFS2 setattr, inode ACL cache helpers, and mount idmap interfaces.

## Risks And Invariants
Deserializer must reject malformed sizes, unknown version, invalid tags, and trailing bytes. Access ACL mode updates must happen before xattr persistence. The code uses `nop_mnt_idmap` for mode update rather than the passed idmap.
