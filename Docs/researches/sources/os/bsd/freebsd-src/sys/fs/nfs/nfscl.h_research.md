# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfscl.h

This header contains small NFS client-side definitions used by the FreeBSD NFSv4 client.

Key behavior:
- Defines `struct nfsv4node`, an allocation-sized extension for an NFSv4 `nfsnode` that stores file-handle length, name length, and contiguous file-handle/name data.
- Defines `NFS4NODENAME()` to locate the node name immediately after the file handle bytes.
- Defines `NFSCL_REQSTART()` as a convenience wrapper around `nfscl_reqstart()` for vnode-based client RPC calls.
- Defines lease/renew conversion macros `NFSCL_RENEW()` and `NFSCL_LEASE()`, currently using a half-lease renew interval.
- Defines `NFSCL_FORCEDISM()` to detect forced unmount state from mount flags and NFS mount private flags.
- Defines client set-attribute flags passed to `nfscl_fillsattr()`, including full attribute send, size zero, size negative-one, rdev-as-size, and new-file handling.
- Defines `NFSCL_DEBUG()` gated by `nfscl_debuglevel`.
- Defines `struct nfscl_reconarg`, which carries minor version and session id for reconnect/session recovery.

Important interactions:
- `NFSCL_REQSTART()` depends on vnode-to-NFS mount/node macros and starts requests with the vnode’s current file handle.
- `NFSCL_FORCEDISM()` is used by lock/session wait paths to break out during forced dismount.
- `NFSSATTR_*` flags are interpreted in `nfscl_fillsattr()`.

Edge cases:
- `struct nfsv4node` uses a one-byte flexible tail pattern and must be allocated large enough for both file handle and name.
- The renew/lease macros are deliberately simple inverses; lease policy changes should keep that relationship in mind.
