# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfskpiport.h

This small port header provides Darwin-style KPI typedefs needed by shared NFS code while building on FreeBSD.

Key behavior:
- Defines `mount_t` as `struct mount *`.
- Defines `vnode_t` as `struct vnode *`.
- Wraps the definitions in `_NFS_NFSKPIPORT_H_` include guards.

Important interactions:
- Lets shared code use portable `mount_t` and `vnode_t` names without changing FreeBSD kernel types.
- Included by NFS port/common headers that retain compatibility naming from the multi-platform NFS code base.

Edge cases:
- This header only aliases types; it does not provide any behavioral compatibility layer.
