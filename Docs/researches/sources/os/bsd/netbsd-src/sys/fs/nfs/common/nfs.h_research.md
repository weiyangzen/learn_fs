# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs.h

## Purpose
Defines shared NFS constants, flags, request descriptors, credential structures, file-handle structures, and helper macros used by client, server, callback, locking, and RPC code.

## Main Constants
- Timeout/retry/window constants for NFS client RPC, callbacks, upcalls, retransmits, read/write/readdir defaults, async daemon limits, uid hash sizes, lease lifetimes, cache high-water marks, and NFSv4 callback port.
- NFSv4 server/client state limits for delegations, layouts, clients, sessions, and locks.
- Attribute bitset word count and macros for supported, get, write, pathconf, statfs, readdirplus, referral, callback-getattr, settable/fillable, equality, nonzero, set/clear/copy operations.

## Main Structures
- `nfsd_addsock_args`, `nfsd_nfsd_args`, `nfsd_nfscbd_args`, `nfscbd_args`, `nfsd_idargs`, and `nfsd_oidargs` define `nfssvc(2)`/daemon/user-id mapping arguments.
- Dump/list structures describe NFSv4 clients, locks, client IDs, lock owners, and callback addresses.
- `nfsreferral` stores referral server-list metadata.
- `nfscred` stores UID and groups associated with acquired stateids.
- `nfssockreq` stores per-connection RPC transport state: address, socket type/protocol/flags, credential, lock bits, mutex, RPC program/version, client handle, and cached auth handle.
- `nfsrv_descript` is the central request/reply XDR descriptor: mbuf chains and positions, socket addresses, proc number, flags, status, xid/cache pointers, file handle, credentials, GSS principal, session/slot data, and server transport.
- `nfsv4_opflag`, `nfsfh`, `nfsrvfh`, `nfsv4lock`, and `nfsslot` define operation metadata, client/server file handles, sleep locks, and NFSv4.1 slot state.

## Main Flags
- Client/server flags for NFS versions, GSS modes, stream sockets, public lookup, implied client IDs, NFSv4.1/session/sequence state, callback direction, reply caching, and no-more-data parsing.
- NFSv4 client flags (`LCL_*`) for callback, GSS, confirmation, cleanup, reclaim, and lease/client state.
- NFS lock/state flags (`NFSLCK_*`) encode access/deny bits, lock/read/write/blocking/test/open/close/release/delegation/reclaim/downgrade/setattr/want states.
- `NFSR_*` bits describe send/receive/reserved-port/local transport state.

## Integration
This is a core include for files in this group: `nfsmount.h` embeds `nfssockreq`; `nfs_commonkrpc.c` operates on `nfsrv_descript` and `nfssockreq`; `nfs_clvnops.c` depends on flags, attr bit macros, timeouts, and file-handle comparisons.

## Risks
- Many macros manually assume `NFSATTRBIT_MAXWORDS == 3`; changing the attribute bitset size requires coordinated macro updates.
- Several structures are ABI-facing through `nfssvc(2)` or daemon interaction; field changes are compatibility-sensitive.
- The file mixes client, server, callback, and syscall concepts, so “small” edits can have broad blast radius.
