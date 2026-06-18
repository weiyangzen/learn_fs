# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nfs.h

This header defines NFS v2 constants used by the bridge.

Key content:
- NFS status codes such as `NFS_OK`, `NFSERR_PERM`, `NFSERR_NOENT`, `NFSERR_STALE`, and `NFSERR_WFLUSH`.
- NFS file types: `NFNON`, `NFREG`, `NFDIR`, `NFBLK`, `NFCHR`, and `NFLNK`.
- NFS mode constants `S_IFMT`, `S_IFDIR`, and `S_IFREG`.
- `NOATTR` sentinel for unset setattr fields.

Important interactions:
- Used by `nfs.c`, `nfsmount.c`, and `nfsserver.c`.
- Constants match RFC 1094-era NFS v2 expectations.

Research notes:
- This header is protocol-definition only.
