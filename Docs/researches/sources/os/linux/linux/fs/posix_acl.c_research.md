# File Research: sources/os/linux/linux/fs/posix_acl.c

## Purpose
Provides generic VFS support for POSIX ACLs: inode ACL caching, ACL allocation/refcounting, validation, permission checks, chmod/create mode transformations, xattr encoding/decoding, idmapped mount handling, and VFS-level ACL get/set/remove operations.

## Main Responsibilities
- Manages cached access/default ACL pointers in inodes.
- Fetches ACLs through filesystem inode operations with sentinel-based race handling.
- Allocates, initializes, clones, validates, and releases ACL objects.
- Converts ACLs to and from traditional Unix mode bits.
- Applies POSIX ACL permission checks with user/group/idmap handling.
- Computes inherited ACLs during file creation and updates ACLs during chmod.
- Converts ACLs between in-memory and xattr/uapi representations.
- Provides VFS ACL set/get/remove helpers with LSM hooks, delegation breaking, ownership checks, and fsnotify.
- Provides simple filesystem helpers for cached in-memory ACLs.

## Key Interfaces
Exports or defines:
- Cache: `get_cached_acl`, `get_cached_acl_rcu`, `set_cached_acl`, `forget_cached_acl`, `forget_all_cached_acls`, `get_inode_acl`.
- Object handling: `posix_acl_init`, `posix_acl_alloc`, `posix_acl_clone`.
- Validation/conversion: `posix_acl_valid`, `posix_acl_equiv_mode`, `posix_acl_from_mode`, `posix_acl_from_xattr`, `posix_acl_to_xattr`.
- Permission/mode: `posix_acl_permission`, `__posix_acl_create`, `__posix_acl_chmod`, `posix_acl_chmod`, `posix_acl_create`, `posix_acl_update_mode`.
- VFS operations: `set_posix_acl`, `vfs_set_acl`, `vfs_get_acl`, `vfs_remove_acl`, `do_set_acl`, `do_get_acl`.
- Simple helpers: `simple_set_acl`, `simple_acl_create`.

## Control Flow and Data Handling
ACL cache access uses inode `i_acl` and `i_default_acl` with RCU/refcount coordination. `__get_acl()` installs an uncached sentinel before invoking filesystem callbacks, so concurrent fetches or invalidations can be detected without corrupting cache state.

ACL validation enforces POSIX ordering and required mask entries. Permission checking walks entries in order, first checking owner, then named users, owning group, named groups, mask, and other. Idmapped mounts are handled through VFS uid/gid conversion helpers during permission checks and user-visible xattr conversion.

Setting ACLs parses the ACL name, translates IDs for idmapped mounts, locks the inode, checks write-xattr permission, invokes LSM hooks, breaks delegations, calls the filesystem `set_acl`, and posts fsnotify/security notifications. Getting ACLs performs LSM checks, rejects unsupported inode types, fetches via cache/filesystem, and converts missing ACLs to `-ENODATA`.

## Dependencies and Integration
Integrates with inode operations (`get_acl`, `get_inode_acl`, `set_acl`), xattr names, user namespaces, idmapped mounts, LSM hooks, fsnotify, delegation handling, and VFS inode locking. Filesystems use these helpers to avoid duplicating ACL semantics.

## Concurrency and Lifetime Notes
ACL objects are refcounted. Cache replacement uses atomic exchange and releases old ACLs unless they are uncached sentinels. VFS set/remove paths hold inode locks and may retry after breaking delegations. RCU paths must not take references unless safe.

## Risks and Review Hotspots
- ACL cache sentinel logic is race-sensitive.
- ID mapping must be correct at the filesystem boundary versus user boundary; mixing mount idmaps with filesystem cache representation would be a security bug.
- `posix_acl_update_mode()` can clear setgid and null out equivalent ACLs; callers must honor modified pointers.
- xattr parsing validates sizes, versions, uid/gid mappings, and ACL structure; relaxing checks can admit invalid on-disk ACLs.
