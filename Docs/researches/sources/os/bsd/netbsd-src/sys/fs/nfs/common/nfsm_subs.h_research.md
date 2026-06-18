# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsm_subs.h

This header defines low-level mbuf/XDR helper macros and inline functions used throughout the NFS code.

Key contents:
- Defines `NFSM_DATAP()` to advance mbuf data pointers.
- `nfsm_build()` appends contiguous space to the current output mbuf, allocating a new mbuf when trailing space is insufficient.
- `NFSM_BUILD()` wraps `nfsm_build()` and casts the result for callers.
- `nfsm_dissect()` and `nfsm_dissect_nonblock()` return contiguous input bytes from the current mbuf chain or call `nfsm_dissct()` for difficult cases.
- `NFSM_DISSECT()` and `NFSM_DISSECT_NONBLOCK()` include standard error handling by setting `EBADRPC` and jumping to `nfsmout`.
- `NFSM_STRSIZ()` parses an XDR string length and validates it against a maximum.
- `NFSM_RNDUP()` rounds XDR lengths to four-byte alignment.

Important dependencies:
- Calls functions implemented in `nfs_commonsubs.c`.
- Assumes functions using these macros have local variables named `nd`, `error`, and `nfsmout`.

Risks and notes:
- These macros intentionally make strong control-flow and local-variable assumptions. They are powerful but fragile outside the established NFS parsing style.
