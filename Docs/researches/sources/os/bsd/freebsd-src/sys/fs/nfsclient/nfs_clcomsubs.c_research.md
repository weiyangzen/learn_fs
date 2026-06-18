# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clcomsubs.c

`nfs_clcomsubs.c` contains client common subroutines for mbuf/uio transfer, reply file-handle and attribute parsing, and NFSv4 client lock helper wrappers.

Key functions and behavior:
- `nfsm_uiombuf()` copies a single-iovec `uio` payload into the current NFS request mbuf chain held by `struct nfsrv_descript`. It supports ordinary mbufs and external-page mbufs, pads to XDR alignment, updates `nd_bpos`/`nd_mb`, and advances the uio.
- `nfsm_uiombuflist()` builds and returns a new mbuf chain from a single-iovec `uio`, optionally using external pages. On user-copy failure it frees the chain and returns `NULL`.
- `nfsm_loadattr()` parses post-op attributes from an NFS reply into `struct nfsvattr`. It dispatches to `nfsv4_loadattr()` for v4, decodes packed `struct nfs_fattr` for v3, and handles v2 quirks including FIFO-as-character-device representation and ctime/usec-as-generation mapping.
- `nfscl_mtofh()` extracts a file handle and optional attributes from NFSv3 or NFSv4 replies. For NFSv4 it expects GetFH and Getattr operation results; for NFSv3 it handles post-op present flags.
- `nfscl_lockinit()`, `nfscl_lockexcl()`, `nfscl_lockunlock()`, and `nfscl_lockderef()` wrap NFSv4 client state/delegation lock initialization, exclusive acquisition, release, and reference dropping/wakeup behavior.

Important integration points:
- Assumes `uio_iovcnt == 1` for mbuf-copy helpers; callers must segment larger scatter/gather writes before calling.
- Uses XDR conversion helpers from `xdr_subs.h` and protocol structs from `nfsproto.h`.
- Attribute parsing feeds cache loading and vnode attribute update paths elsewhere.
- Lock dereference uses the client state mutex macros from `nfsport.h`.

Research notes:
- This file sits between RPC marshalling/parsing macros and higher-level vnode operations.
- Error paths are important because partial mbuf/uio advancement and copyin failures can otherwise corrupt request construction.
