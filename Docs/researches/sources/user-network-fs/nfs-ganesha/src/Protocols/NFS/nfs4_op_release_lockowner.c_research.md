# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_release_lockowner.c

## Purpose
Implements NFSv4.0 `RELEASE_LOCKOWNER`. It validates the clientid, reserves or expires the lease, resolves the lock owner, releases it if present, and updates the client lease.

## Important APIs, Types, and Functions
- `nfs4_op_release_lockowner` handles the operation.
- Uses `nfs_client_id_get_confirmed`, `reserve_lease_or_expire`, `convert_nfs4_lock_owner`, `create_nfs4_owner`, `release_lock_owner`, `update_lease_simple`, and reference release helpers.
- `nfs4_op_release_lockowner_Free` is a no-op.

## Control Flow
The handler rejects minorversion greater than 0 with `NFS4ERR_NOTSUPP`, looks up a confirmed clientid, reserves the lease, converts the wire lock owner to a SAL owner name, looks up or creates the owner in lookup-only semantics, releases it when found, drops owner/client refs, updates the lease, and returns converted status.

## State and Persistence Behavior
Mutates in-memory lock-owner state by releasing an owner and may expire a client lease if stale. It updates the client's lease time on normal completion. It does not alter filesystem data.

## Dependencies and Integration Points
Depends on NFSv4.0 clientid and lease management, SAL owner lookup/refcounting, and lock-owner release semantics. This op is intentionally not available in v4.1 because sessions replace its use.

## Risks
Owner lookup behavior is subtle: unknown lock owners are treated as success. Lease reservation must be balanced with reference releases. `create_nfs4_owner` is used as a find/create API with flags that need to preserve protocol semantics.

## Test Signals
Test v4.1 rejection, stale/unknown/expired clientids, unknown lock owner success, lock owner with outstanding locks, release success, lease update, and concurrent release against lock-owner deletion.
