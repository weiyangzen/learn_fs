# File Research: sources/os/linux/linux-stable/fs/nfs/delegation.h

## Purpose

`delegation.h` defines the NFSv4 delegation structure, delegation flag bits, exported delegation management APIs, delegation-related NFSv4 procedure hooks, and small inline helpers for checking delegated capabilities.

## Main Contents

- `struct nfs_delegation` fields:
  - hash/list membership for filehandle lookup and server traversal
  - credential pointer
  - associated inode pointer
  - NFSv4 stateid
  - delegation type and page-modification limit
  - delegated change attribute and expiry-test generation
  - flags, refcount, spinlock, queue entry, and RCU head
- Flag bits for reclaim, return-on-close, reference tracking, active return, revoked state, expired-test state, and delegated time attributes.
- Public APIs for setting, reclaiming, returning, evicting, finding, expiring, marking, reaping, and testing delegations.
- Procedure hooks implemented elsewhere for `DELEGRETURN`, open recall, and lock recall.
- Stateid copy/refresh helpers and delegation validity checks.
- Inline helpers for read/write delegation, delegated attributes, delegated atime/mtime, directory delegation request/check, and write flush-on-close behavior.
- Declaration of the `directory_delegations` module parameter and delegation hash allocator.

## Integration Points

This header is consumed by NFS inode, open, lock, callback, state recovery, and attribute paths. It conditionally exposes most functionality under `CONFIG_NFS_V4`, while generic delegated attribute helpers remain available to call through `NFS_PROTO(inode)->have_delegation`.

## API and State Notes

Delegation references returned by functions such as `nfs4_get_valid_delegation()` must be dropped with `nfs_put_delegation()`. Optional credential outputs from `nfs4_copy_delegation_stateid()` are returned with an acquired credential reference. `NFS_DELEGATION_FLAG_TIME` asks `have_delegation` implementations to require delegated time-attribute support.

## Testing Focus

Review callers for correct reference/credential release, correct use of read versus write delegation checks, safe directory delegation requests only on directories, and correct behavior when `CONFIG_NFS_V4` is disabled.
