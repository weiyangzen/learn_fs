# File Research: sources/os/linux/linux/fs/nfs/nfs3acl.c

## Purpose
Implements NFSv3 POSIX ACL operations using the Sun NFSACL side protocol.

## Key Functions
- `nfs3_get_acl()` fetches access/default ACLs, handles RCU refusal, revalidates inode change state, prepares race-safe ACL cache sentinels, calls GETACL, updates inode attributes, and caches or releases returned ACLs.
- `__nfs3_proc_setacls()` validates ACL support and entry counts, allocates pages when needed, sends SETACL, zaps access/ACL caches, and refreshes inode attributes.
- `nfs3_proc_setacls()` treats `-EOPNOTSUPP` as non-fatal for create/mkdir/mknod post-processing.
- `nfs3_set_acl()` coordinates access/default ACL pairs for directories and synthesizes an access ACL from mode when clearing.
- `nfs3_listxattr()` lists POSIX ACL xattr names only when corresponding ACLs exist.

## Edge Handling
- Disables server ACL capability on protocol-not-supported failures.
- Caps ACL entries at `NFS_ACL_MAX_ENTRIES`.
- Frees XDR-allocated pages from GETACL and SETACL page allocations.
- Uses POSIX ACL cache sentinel helpers to avoid racing with generic ACL cache population.

## Research Notes
This file is optional behind `CONFIG_NFS_V3_ACL`. Its behavior is tightly coupled to `nfs3xdr.c` ACL XDR procedures and `nfs3client.c` ACL RPC client setup.
