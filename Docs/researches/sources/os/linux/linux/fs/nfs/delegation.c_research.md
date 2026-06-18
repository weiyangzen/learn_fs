# File Research: sources/os/linux/linux/fs/nfs/delegation.c

## Purpose
Implements NFSv4 file and directory delegation lifecycle management. It tracks delegated state per inode, validates delegation availability, handles recalls/returns/revocation, maintains delegation LRU/return queues, supports reboot/reclaim handling, and exposes helpers for using delegation stateids.

## Main Responsibilities
- Allocate, attach, update, detach, revoke, and free `nfs_delegation` objects.
- Check read/write/time delegation availability.
- Return delegations synchronously or asynchronously.
- Reclaim delegated open and lock state during delegation return.
- Maintain per-server delegation hash tables and lists.
- Expire unused, unreferenced, revoked, or unclaimed delegations.
- Handle server reboot/lease-expiry delegation validation.
- Copy or refresh delegation stateids for NFS operations.
- Enforce a delegation watermark with LRU-based return.

## Key Functions
- `nfs_inode_set_delegation()` attaches a new delegation or updates/replaces an existing one.
- `nfs_inode_reclaim_delegation()` updates delegation state after reclaim.
- `nfs4_have_delegation()` and `nfs4_check_delegation()` test delegation presence with optional reference marking.
- `nfs_async_inode_return_delegation()` marks a matching delegation for state-manager return after callback recall.
- `nfs4_inode_return_delegation()` synchronously returns a delegation and flushes dirty regular-file data.
- `nfs4_inode_set_return_delegation_on_close()` and `_on_close()` defer return until open files close.
- `nfs_client_return_marked_delegations()` drains return queues from the state manager.
- `nfs_delegation_find_inode()` locates an inode by filehandle for callback recall.
- `nfs_remove_bad_delegation()`, `nfs_delegation_mark_returned()`, and `nfs_revoke_delegation()` handle invalid or returned stateids.
- `nfs_delegation_mark_reclaim()` and `nfs_delegation_reap_unclaimed()` support reboot recovery.
- `nfs_reap_expired_delegations()` tests and frees delegations after lease-expiry suspicion.
- `nfs4_copy_delegation_stateid()` and `nfs4_refresh_delegation_stateid()` provide stateid helpers to operation paths.

## Delegation Attachment Flow
`nfs_inode_set_delegation()` allocates a delegation, initializes stateid/type/cred/change attribute/flags, then under `cl_lock` either attaches it to inode/server/hash lists, updates an existing delegation with the same stateid identity, rejects a duplicate, or replaces an older delegation. It also invalidates cached inode attributes when change data was not revalidated.

## Delegation Return Flow
Return begins with `nfs_start_delegation_return()`, which grabs a valid delegation and sets `NFS_DELEGATION_RETURNING`. `nfs_end_delegation_return()` breaks leases, claims delegated opens and locks for regular files, waits for recovery if synchronous, then sends `DELEGRETURN`. Delayed returns are requeued and marked with `NFS4CLNT_DELEGRETURN_DELAYED`.

## Lists and Hashes
- `server->delegations` tracks attached delegations.
- `server->delegations_return` queues delegations to return.
- `server->delegations_lru` tracks closed delegations for pressure return.
- `server->delegations_delayed` holds delayed returns.
- `server->delegation_hash_table` maps filehandles to delegations for callback lookup.

## Locking and Lifetime
- `clp->cl_lock` protects inode delegation pointer attach/detach.
- `server->delegations_lock` protects return/LRU/delayed queues.
- Each delegation has its own spinlock for inode pointer, stateid, cred, and flags-sensitive updates.
- Delegations are refcounted and freed with `kfree_rcu()`.
- Lookup paths use RCU and `igrab()`/`nfs_sb_active()` to safely return inodes.

## Notable Details
- Directory delegations are enabled by default via module parameter.
- `delegation_watermark` defaults to 5000 and drives LRU return pressure.
- Delegated time attributes are tracked through `NFS_DELEGATION_DELEGTIME`.
- Revocation marks stateid invalid, decrements active delegation count, and may clear delegated verifier state.
- If the server reboots during expired-delegation testing, the code re-marks work and returns `-EAGAIN`.

## Risks and Edge Cases
- Delegation replacement handles broken servers that hand out duplicate delegations; write upgrades are specially tolerated.
- Stateid sequence comparisons decide whether revocation/returned notifications apply, so stale callback data is ignored.
- Some return paths cannot flush dirty data because they run in the state manager and could deadlock during recovery.
- Delegation queue reference counts must stay balanced when moving between list states.

## Integration Points
Used by callback recall/getattr handlers, NFSv4 open/lock recovery code, inode attribute delegation helpers, state manager recovery, pNFS recall-any paths, and NFS operation code that wants to use delegation stateids.
