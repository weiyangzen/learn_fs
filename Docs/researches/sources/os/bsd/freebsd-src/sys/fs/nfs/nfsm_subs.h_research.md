# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsm_subs.h

This header defines the low-level mbuf-chain build/dissect macros used throughout the NFS protocol encoder and decoder.

Key behavior:
- Defines `NFSM_DATAP()` to advance an mbuf data pointer.
- Provides inline `nfsm_build()` to reserve contiguous output space from the current `nfsrv_descript` mbuf. It appends a new mbuf when normal trailing space is insufficient, or allocates a new external-page mbuf when ext-page space is insufficient.
- Defines `NFSM_BUILD()` as the typed assignment wrapper around `nfsm_build()`.
- Provides inline `nfsm_dissect()` and `nfsm_dissect_nonblock()` to return contiguous input bytes from the current descriptor position, falling back to `nfsm_dissct()` when data spans mbufs.
- Defines `NFSM_DISSECT()` and `NFSM_DISSECT_NONBLOCK()` wrappers that jump to `nfsmout` with `EBADRPC` on parse failure.
- Defines `NFSM_STRSIZ()` to parse an XDR string length and enforce a caller-provided maximum.
- Defines `NFSM_RNDUP()` for 4-byte XDR alignment.

Important interactions:
- These macros assume local variables named `nd`, `error`, `tl`, and `nfsmout` in many call sites.
- The heavy fallback and ext-page support are implemented in `nfs_commonsubs.c`.
- Used by client RPC builders, server reply builders, and all common XDR parsers.

Edge cases:
- The macros are intentionally specialized for NFS mbuf cursor state and are unsafe as general mbuf utilities.
- `nfsm_build()` panics if a requested normal-mbuf build size exceeds `MLEN`.
- Ext-page and non-ext-page mbuf construction paths must not be mixed for the same descriptor.
