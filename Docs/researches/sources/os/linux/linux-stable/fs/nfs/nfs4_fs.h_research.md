# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4_fs.h

This is the central internal NFSv4 client header for filesystem-specific NFSv4 definitions, state structures, minor-version operations, and cross-file declarations.

Main content:
- Minor version bounds:
  - `NFS4_MIN_MINOR_VERSION`
  - `NFS4_MAX_MINOR_VERSION`
- NFSv4 client state bits:
  - Lease recovery, reclaim, session reset, server-scope mismatch, delegation expiration, callback recall states, migration states, and manager scheduling bits.
- Sequence ID support:
  - `struct nfs_seqid_counter`
  - `struct nfs_seqid`
  - `nfs_confirm_seqid()`
- State-owner and state tracking:
  - `struct nfs4_state_owner`
  - `struct nfs4_lock_state`
  - `struct nfs4_state`
  - State flags for open modes, delegation, reclaim, recovery failure, lock notification, and server-side-copy roles.
- `struct nfs4_exception`
  - Carries state, inode, stateid, timeout, retransmit count, privilege/delay/recovery/retry flags, and interruptibility for recovery loops.
- Operation vtables:
  - `struct nfs4_minor_version_ops`
  - `struct nfs4_sequence_slot_ops`
  - `struct nfs4_state_recovery_ops`
  - `struct nfs4_state_maintenance_ops`
  - `struct nfs4_mig_recovery_ops`

Important declarations:
- NFSv4 procedure, state, recovery, session, migration, namespace, idmapping, and xattr functions.
- `nfs4_state_protect()` helpers for SP4 machine credential protection.
- Session and trunking declarations.
- XDR procedure table and v4.2 xattr overhead constants.
- Optional sysctl and xattr-cache stubs based on config.

Inline helpers:
- Data-server role checks:
  - `is_ds_only_client()`
  - `is_ds_client()`
- Stateid operations:
  - `nfs4_stateid_copy()`
  - `nfs4_stateid_match()`
  - `nfs4_stateid_match_other()`
  - `nfs4_stateid_is_newer()`
  - `nfs4_stateid_is_next()`
  - `nfs4_stateid_match_or_older()`
  - `nfs4_stateid_seqid_inc()`
- Open-state validity checks.
- Stubs for non-NFSv4 builds.

Role in this group:
- `nfs42proc.c`, `nfs42xattr.c`, `nfs4client.c`, `nfs4file.c`, `nfs4getroot.c`, `nfs4idmap.c`, `nfs4namespace.c`, `nfs4renewd.c`, and `nfs4session.c` all rely on this header for shared state and declarations.
- It defines the common state/recovery vocabulary used throughout these files.

Risk areas:
- State flags and stateid helper semantics are cross-cutting; small changes can affect open, lock, delegation, copy, and recovery paths.
- Config-guarded stubs must match real function signatures closely enough to keep callers correct across build options.
