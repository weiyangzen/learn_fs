# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsmountrpc.h

## Purpose

`nfsmountrpc.h` declares helper routines used during NFS root/diskless boot mount RPC discovery and option parsing.

## Main Contents

- `md_mount()` performs mount-daemon RPC lookup for a path and returns a file handle, handle size, and adjusted NFS args.
- `md_lookup_swap()` performs similar lookup for an NFS swap path.
- `nfs_mountopts()` parses/sets NFS mount options into `struct nfs_args`.
- `setfs()` parses/sets server address/path information.

## Notable Details

- This header has no include guard in the read file.
- It is specific to mount-time support, not normal vnode operation.
- The declarations use IPv4 `struct sockaddr_in`, matching diskless-root comments that this path is AF_INET-only.

## Integration

Consumed by `nfs_vfsops.c` for `nfs_mountdiskless()` when no loader-provided root/swap file handle is available, with implementations in `nfs_mountrpc.c`.
