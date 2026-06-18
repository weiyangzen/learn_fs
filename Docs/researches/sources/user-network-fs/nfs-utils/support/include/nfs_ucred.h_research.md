# sources/user-network-fs/nfs-utils/support/include/nfs_ucred.h

## Purpose
Declares credential helpers used to execute filesystem operations under NFS request credentials and export squash policy.

## Important APIs, Types, and Functions
`struct nfs_ucred`, `nfs_ucred_get()`, group squash/reload helpers, `nfs_ucred_swap_effective()`, and inline free/init/free-groups helpers.

## Control Flow
Callers derive credentials from RPC requests and export options, adjust supplemental groups, swap process effective credentials around sensitive operations, then restore and free.

## State and Persistence Behavior
Credential objects own a heap group array. Effective uid/gid/group state is process-global while swapped, so callers must restore carefully.

## Dependencies and Integration Points
Used by `nfsd_path.c` openat wrappers and auth/export code. Depends on RPC request and `exportent` types.

## Risks and Edge Cases
Credential swapping can affect all threads if not serialized. Ownership of saved credentials must be followed exactly.

## Test Signals
Test squash rules, group reload, swap/restore on success and failure, and `nfsd_cred_openat()` permission behavior.
