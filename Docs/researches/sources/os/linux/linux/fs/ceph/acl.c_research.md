# File Research: sources/os/linux/linux/fs/ceph/acl.c

## Purpose
Implements CephFS POSIX ACL get/set support and ACL initialization payload preparation for newly created inodes.

## Main Elements
- `ceph_set_cached_acl()`: caches or forgets ACLs depending on whether the inode currently has `CEPH_CAP_XATTR_SHARED`.
- `ceph_get_acl()`: fetches ACL xattrs through `__ceph_getxattr()`, retries `-ERANGE` up to ten times, converts xattr bytes to `struct posix_acl`, and updates the VFS ACL cache.
- `ceph_set_acl()`: rejects snapshot inodes, validates access/default ACL type, updates mode through `posix_acl_update_mode()`, serializes ACLs to xattr format, applies mode changes with `__ceph_setattr()`, writes ACL xattrs with `__ceph_setxattr()`, and rolls mode back if xattr write fails.
- `ceph_pre_init_acls()`: computes inherited ACLs for new inode creation, drops equivalent access ACLs, encodes one or two ACL xattr records into a Ceph pagelist, and stores ACL pointers plus pagelist in `ceph_acl_sec_ctx`.
- `ceph_init_inode_acls()`: seeds the new inode ACL cache from the prepared ACL/security context.

## Dependencies And Integration
Uses Linux POSIX ACL helpers, Ceph xattr and setattr routines, Ceph capability state, Ceph pagelists for MDS request payloads, and Ceph inode/client helpers from `super.h` and `mds_client.h`.

## Risk Notes
ACL caching is valid only when xattr-shared capabilities are issued; otherwise cached ACLs are forgotten. `ceph_set_acl()` changes mode before setting the ACL xattr and attempts rollback on xattr failure. `ceph_pre_init_acls()` transfers ACL ownership to the caller on success, so error paths must release ACLs, temporary xattr buffers, and pagelists.
