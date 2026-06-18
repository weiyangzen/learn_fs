# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs.h

## Purpose

`nfs.h` is a central FreeBSD NFS header defining timing constants, sizing limits, `nfssvc(2)` argument structures, NFSv4 client/server state flags, attribute and operation bitset helpers, socket/request descriptors, file-handle structures, NFS request descriptor layout, session slots, ACL support constants, and assorted NFS utility macros.

## Constants And Tunables

The header defines client/server timing defaults such as `NFS_TICKINTVL`, `NFS_TIMEO`, minimum/maximum timeout values, TCP timeout, callback timeout/retry counts, upcall timeout/retry counts, soft-mount retry defaults, delegation return wait, and NFSv4 lease-related constants. It also defines I/O sizing defaults (`NFS_WSIZE`, `NFS_RSIZE`, `NFS_READDIRSIZE`), read-ahead/async daemon limits, hash-table sizes, state/cache high-water marks, pNFS device limits, and maximum NFSv4 owner/group string length.

NFSv4 root constants reserve a synthetic FSID/inode/generation for the v4 pseudo-root. Server/client cache and state watermarks are used by other NFS server and client code to bound memory/state growth.

## nfssvc And Userland ABI Structures

The header declares several structures passed through the `nfssvc(2)` interface or related NFS userland daemons:

- `nfsd_addsock_args`, `nfsd_nfsd_args`, and old `nfsd_nfsd_oargs` for nfsd startup and socket/service configuration, including pNFS DS metadata in the newer structure.
- `nfsd_pnfsd_args` and `PNFSDOP_*` operations for pNFS data-server management.
- `nfsd_nfscbd_args`, `nfscbd_args`, and `nfsuserd_args` for callback daemon and nfsuserd configuration.
- `nfsd_oidargs`, `nfsuserd_args`, `nfsd_clid`, dump-list/client/lock structures, and `nfsreferral` for id mapping, stats/dump operations, lock/client reporting, and referrals.

## NFSv4 State Flags

`LCL_*` flags describe NFSv4 server client state such as confirmation, callback transport, callback liveness, GSS modes, admin revoke, reclaim completion, NFSv4.1/v4.2 support, TLS callback state, and machine-credential state.

`NFSLCK_*` flags describe open/share/lock/delegation state. The access and deny bits are intentionally ordered because later code shifts between read/write access, deny, and lock bits. Flags cover open, close, lock, unlock, blocking, reclaim, delegation, downgrade, release, setattrs, and wanted delegation types.

## Attribute And Operation Bitsets

`nfsattrbit_t` is a fixed three-word bitset with macros for zero/copy/test/set/clear operations and common attribute masks. Macros build masks for supported attributes, fillable attributes, settable attributes, GETATTR, weak cache consistency, write GETATTR, callback GETATTR, pathconf, statfs, rootfs, readdirplus, and referral attributes. Several macros conditionally remove NFSv4.1 or NFSv4.2 attributes based on descriptor flags.

`nfsopbit_t` is a fixed three-word operation bitset with analogous zero/copy/test/set/clear helpers for NFSv4 operation support.

The header comments explicitly warn that these macros must be updated if the bitset word count changes.

## Runtime Structures

`struct nfscred` stores the uid and groups used when stateids are acquired. `struct nfssockreq` records socket address, socket type/protocol/flags, credential, lock bits, mutex, RPC program/version, RPC client, cached AUTH handle, and server principal name storage. `struct nfsrv_descript` is the central request/reply descriptor for NFS client, server, and callback code; it tracks mbuf chains, current XDR positions, flags, procedure number, reply status, credentials, GSS principal, TCP/socket refs, NFSv4 session IDs and slot sequencing, current stateids, max request/response sizes, external-page build state, and allowed operations for machine credentials.

Other structures include client/server file handles (`nfsfh`, `nfsrvfh`), NFSv4 sleep lock state (`nfsv4lock`), NFSv4.1 sequence slots (`nfsslot`), GSS mechanism descriptors, network-address unions, and request-queue heads.

## Descriptor Flags

`ND_*` flags encode protocol version, security mode, reply-cache behavior, public lookup, GSS principal use, same TCP connection, implied client ID, no-more-data state, callback/client direction, NFSv4.1/v4.2/session/slot state, pNFS data-server state, current-stateid handling, external-page mbufs, TLS modes, relockup state, and machine credentials. These flags are consumed heavily by XDR builders/parsers and `newnfs_request()`.

## Dependencies

This header bridges kernel-only types from RPC, sockets, mbufs, credentials, vnodes, mount state, NFS XDR constants, ACL constants, and pNFS/session state defined in other NFS headers. It is intentionally shared across NFS client, server, callback, and common-port code.

## Invariants And Risks

- Fixed-size bitset macros must stay synchronized with protocol maximum attribute/op numbers.
- Many state flags are protocol-coupled; changing flag values can break shift-based lock/open/share tests.
- `struct nfsrv_descript` is shared across many layers, so flag interpretation and mbuf cursor ownership must be consistent.
- `nfssvc` structures are ABI-facing and must preserve layout compatibility for old and new userland callers.
