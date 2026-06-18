# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3acl.c

## Purpose
Implements NFSv3 POSIX ACL get/set/list xattr support using the separate Sun NFSACL v3 RPC program.

## ACL Cache Race Handling
- `nfs3_prepare_get_acl()`, `nfs3_complete_get_acl()`, and `nfs3_abort_get_acl()` use POSIX ACL sentinel logic to coordinate with VFS ACL caching.
- This mirrors `fs/posix_acl.c:get_acl()` behavior to avoid races where multiple readers fill the same ACL cache.

## Getting ACLs
- `nfs3_get_acl(struct inode *inode, int type, bool rcu)`
  - Rejects RCU mode with `-ECHILD`.
  - Requires `NFS_CAP_ACLS`.
  - Revalidates inode change state first.
  - Requests access ACL only when explicitly asked; requests default ACL for directories.
  - Allocates fattr, prepares cache sentinels, sends `ACLPROC3_GETACL`, frees any XDR-allocated pages, and refreshes inode attributes.
  - Disables ACL capability on protocol unsupported errors.
  - Normalizes trivial/empty access ACLs to `NULL`.
  - Updates or forgets access/default ACL caches based on response mask.

## Setting ACLs
- `__nfs3_proc_setacls()`
  - Validates capability and maximum ACL entry counts.
  - Computes XDR ACL size and allocates pages if larger than inline buffer.
  - Sends `ACLPROC3_SETACL`.
  - Zaps access and ACL caches.
  - Refreshes inode attributes on success.
  - Disables ACL capability on unsupported errors.
- `nfs3_proc_setacls()`
  - Treats `-EOPNOTSUPP` as success for callers that can proceed without server ACL support.
- `nfs3_set_acl()`
  - Handles VFS `set_acl` for access/default ACLs.
  - For directories, fetches the complementary ACL so both access and default ACL state can be sent together.
  - If access ACL is removed, synthesizes ACL from inode mode before sending.

## Listing xattrs
- `nfs3_list_one_acl()` checks whether a given ACL exists and appends its xattr name.
- `nfs3_listxattr()` lists POSIX ACL access and default names when present, respecting buffer size and returning `-ERANGE` as needed.

## Research Notes
This file handles policy above XDR: cache coherency, capability disabling after unsupported responses, VFS ACL semantics, and the requirement to send access/default ACLs together for directories.
