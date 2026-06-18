# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/Makefile

## Role

Builds the DragonFly NFS kernel module.

## Contents

- Sets `KMOD=nfs`.
- Lists NFS module sources including client BIO, node, Kerberos, server, socket, service cache, syscall, VFS, IOD, XDR helper, and vnode operation files.
- Includes generated option headers: `opt_inet.h`, `opt_nfs.h`, `opt_bootp.h`, and `opt_nfsroot.h`.
- Defines `NFS_INET?=1`.
- Generates `opt_inet.h`, writing `#define INET 1` when `NFS_INET` is enabled.
- Includes `<bsd.kmod.mk>`.

## Implementation Notes

- The module build assumes INET support by default because the NFS code in this tree is IPv4-oriented.
- BOOTP/NFS-root option headers are named as build inputs even though this small Makefile only generates `opt_inet.h`.

## Dependencies

Depends on DragonFly kernel module build infrastructure and the NFS source files named in `SRCS`.

## Research Notes

This file is a compact build manifest. It shows that the NFS IOD code is built into the NFS module along with both client and server implementations.
