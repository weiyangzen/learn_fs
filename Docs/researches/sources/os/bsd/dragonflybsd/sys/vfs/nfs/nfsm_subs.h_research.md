# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsm_subs.h

## Purpose

`nfsm_subs.h` declares the NFS marshalling state machine, helper macros, `struct nfsm_info`, and all exported mbuf/XDR helper functions implemented in `nfsm_subs.c`.

## Main Contents

- `enum nfsm_state` defines request state-machine phases:
  - setup, auth, try, wait reply, process reply, done.
- `struct nfsm_info` holds:
  - mbuf construction/parsing pointers (`mb`, `md`, `mrep`, `mreq`, `bpos`, `dpos`),
  - v2/v3 flag,
  - request state-machine fields (`procnum`, vnode, thread, credentials, `nfsreq`, `nfsmount`, error),
  - optional async BIO completion data and writerpc commit state.
- Error-flow macros:
  - `NULLOUT`, `NEGATIVEOUT`, `NEGKEEPOUT`, `NEGREPLYOUT`, and `ERROROUT` standardize `goto nfsmout` cleanup patterns.
- Function prototypes cover request/reply building, file handles, attributes, WCC, strings, uio/bio conversion, mbuf skipping, server reply attributes, and `nfs_request()`.
- `nfsm_clget()` lazily extends mbuf clusters during server reply construction.
- `nfsm_rndup()` rounds XDR fields to 4-byte boundaries.
- `NFSV3_WCCRATTR` and `NFSV3_WCCCHK` select WCC interpretation behavior.

## Notable Details

- The macros assume caller-local variables named `error`, `info`, `nfsd`, and/or `slp` depending on macro.
- `struct nfsm_info` is shared by synchronous vnode RPCs, async BIO RPCs, and server-side encoding paths.
- The header is intentionally low-level and dangerous outside the NFS code because helpers mutate mbuf chains and cleanup ownership.

## Integration

Included by most NFS client/server implementation files. It provides the common ABI between high-level NFS operations and the request state machine in `nfs_socket.c`.
