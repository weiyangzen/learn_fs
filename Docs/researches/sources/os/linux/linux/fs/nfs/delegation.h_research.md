# File Research: sources/os/linux/linux/fs/nfs/delegation.h

## Purpose
Declares NFSv4 delegation data structures, flags, and public APIs for delegation management and delegated attribute checks.

## Main Contents
- `struct nfs_delegation` definition:
  - hash/list membership
  - credential pointer
  - inode pointer
  - delegation stateid
  - delegation type
  - page modification limit
  - change attribute
  - test generation
  - flags
  - refcount
  - spinlock
  - RCU head
- Delegation flag enum:
  - reclaim needed
  - return-if-closed
  - referenced
  - returning
  - revoked
  - test-expired
  - delegated time support
- Public delegation lifecycle, recall, expiration, reclaim, and stateid helper declarations.

## Inline Helpers
- `nfs_have_read_or_write_delegation()`
- `nfs_have_write_delegation()`
- `nfs_have_delegated_attributes()`
- `nfs_have_delegated_atime()`
- `nfs_have_delegated_mtime()`
- `nfs_request_directory_delegation()`
- `nfs_have_directory_delegation()`

## Configuration
Declares `directory_delegations`, implemented as a module parameter in `delegation.c`.

## Integration Points
Included by NFS inode, callback, open, lock, state recovery, and attribute paths that need to test or manipulate NFSv4 delegated state.
