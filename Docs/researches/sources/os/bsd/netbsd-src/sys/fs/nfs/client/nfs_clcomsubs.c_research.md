# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clcomsubs.c

This file contains common client-side NFS request/reply helpers: RPC request construction, mbuf/uio copying, attribute decoding, file-handle extraction, directory-cookie lookup, NFSv4 stateid serialization, and small NFSv4 lock wrappers.

Key entry points:
- `nfscl_reqstart()` initializes an `nfsrv_descript` and starts an NFSv2/v3/v4 request mbuf chain.
- `nfsm_uiombuf()` copies a single-iovec `uio` into an mbuf chain, using clusters for larger writes and XDR padding.
- `nfsm_loadattr()` decodes file attributes from NFSv2, NFSv3, or NFSv4 reply data into `struct nfsvattr`.
- `nfscl_getcookie()` maps a logical directory byte offset to an NFS directory cookie and optionally grows the cookie map.
- `nfscl_mtofh()` extracts a returned file handle and optional attributes from NFS replies.
- `nfsm_stateidtom()` serializes NFSv4 state IDs, including all-zero, all-one, and seqid-zero variants.
- `nfscl_lockinit()`, `nfscl_lockexcl()`, `nfscl_lockunlock()`, and `nfscl_lockderef()` wrap client NFSv4 owner/delegation lock bookkeeping.

Important behavior:
- `nfsv4_opmap[]` maps internal procedure numbers to first NFSv4 operation, operation count, and compound tag.
- `nfs_bigrequest[]` chooses clustered request mbufs for procedures with large request payloads, notably writes and some create/write-to-DS operations.
- NFSv4 request construction adds `SEQUENCE`, `PUTFH`, and sometimes pre-op `GETATTR` operations based on `nfsv4_opflag[]` requirements.
- Attribute parsing handles version-specific details such as NFSv2 FIFO encoding, NFSv3 device numbers, hyper-sized file lengths, and NFSv4 delegated parsing through `nfsv4_loadattr()`.
- Directory cookies are stored in linked `struct nfsdmap` chunks of `NFSNUMCOOKIES`.

Dependencies:
- Relies heavily on NFS mbuf macros from `nfsport.h`, XDR helpers, `nfsv4_opflag[]`, type mapping tables, and global stats.
- Used by the NFS RPC operation implementations to avoid duplicating request start and reply decode boilerplate.

Research notes:
- This file is protocol glue, not policy. Bugs here would affect request layout, reply decoding, or directory offset traversal across many NFS operations.
- `nfsm_uiombuf()` explicitly supports only `uio_iovcnt == 1`, matching the direct comment in `nfs_clbio.c` that write RPC paths cannot handle multi-iovec writes directly.
