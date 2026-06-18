# File Research: sources/os/linux/linux/fs/nfs/nfs4_fs.h

This is the central internal NFSv4 client header for filesystem-specific NFSv4 definitions, state structures, minor-version operation tables, and cross-file declarations.

Main content:
- Minor-version bounds derive from `CONFIG_NFS_V4_0` and `CONFIG_NFS_V4_2`.
- NFSv4 client state bits cover manager state, lease recovery, reclaim, session reset, delegation recall/expiration, migration, lease-moved recovery, and delayed delegation return.
- Sequence ID support is represented by `struct nfs_seqid_counter`, `struct nfs_seqid`, and `nfs_confirm_seqid()`.
- State-owner and state tracking structures include `struct nfs4_state_owner`, `struct nfs4_lock_state`, and `struct nfs4_state`.
- `struct nfs4_exception` carries state, inode, stateid, timeout/retransmit data, privileged/recovery/retry flags, and interruptibility for recovery loops.
- Operation vtables include minor-version ops, sequence slot ops, state recovery ops, state maintenance ops, and migration recovery ops.

Important declarations:
- NFSv4 procedure, state, recovery, session, migration, namespace, idmapping, and xattr functions.
- `nfs4_state_protect()` and `nfs4_state_protect_write()` helpers for SP4 machine credential protection.
- Procedure table declarations, fattr/statfs/pathconf/fsinfo/fs_locations bitmaps, stateid constants, and NFSv4.2 xattr overhead constants.
- Optional sysctl and NFSv4.2 xattr-cache declarations/stubs based on config.

Inline helpers:
- `is_ds_only_client()` and `is_ds_client()` identify pNFS data-server roles from exchange flags.
- Stateid helpers copy, compare full stateids, compare only the opaque portion, compare sequence freshness, handle wraparound increment, and check "match or older" semantics.
- `nfs4_valid_open_stateid()` and `nfs4_state_match_open_stateid_other()` provide small shared checks for open state recovery paths.
- SP4 helpers switch RPC client/credential to machine credentials for protected cleanup, pNFS cleanup, stateid operations, or writes; protected writes may force `NFS_FILE_SYNC` when commit is not machine-credential protected.

Role in this group:
- `nfs42proc.c`, `nfs42xattr.c`, `nfs4client.c`, `nfs4file.c`, `nfs4getroot.c`, `nfs4idmap.c`, `nfs4namespace.c`, `nfs4renewd.c`, and `nfs4session.c` all rely on this header for shared state and declarations.
- It defines the vocabulary and contracts for stateids, sessions, recovery, migration, and NFSv4.2 xattr caching.

Risk areas:
- State flags and stateid helper semantics are cross-cutting; small changes can affect open, lock, delegation, copy, pNFS, and recovery paths.
- Config-guarded stubs must match real function signatures and side-effect expectations.
- SP4 credential switching is security-sensitive and affects cleanup and write stability behavior.
