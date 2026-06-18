# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/rpcv2.h

This header defines Sun RPC version 2 constants used by the DragonFly NFS implementation. It includes protocol version IDs, authentication flavor numbers, RPC message/reply status codes, authentication failure codes, fixed header sizes, mountd/NFS program numbers, and mount RPC limits.

It also defines Kerberos-v4-related RPC verifier structures: `nfsrpc_fullverf`, `nfsrpc_fullblock`, and `nfsrpc_nickverf`, plus explicit byte-size constants that must match their wire layout. The `NFSKERB` branch is effectively disabled with an `XXX` placeholder, while the non-Kerberos path typedefs tiny placeholder key arrays.

Key constants include `RPC_VER2`, `RPCAUTH_UNIX`, `RPCAUTH_KERB4`, `RPC_CALL`, `RPC_REPLY`, `RPCPROG_MNT`, `RPCPROG_NFS`, `RPCX_FULLVERF`, `RPCX_FULLBLOCK`, and Kerberos service/TTL/skew macros.

Research notes: this is wire-format ABI material. Changes affect NFS client/server RPC framing and should be treated as protocol compatibility changes.
