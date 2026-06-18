# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfskpiport.h

This header provides generic KPI compatibility definitions used by the imported NFS code.

Key contents:
- Defines `mount_t` as `struct mount *`.
- Provides `vfs_statfs()`, `vfs_flags()`, `vnode_mount()`, and `vnode_vtype()` macros.
- Defines `mbuf_t` and wrapper macros for freeing, data access, length, next pointer, packet header length, and packet header receive interface.
- Provides user-address and uio helper macros such as `CAST_USER_ADDR_T()`, `uio_uio_resid()`, `uio_iov_base_add()`, and `uio_iov_len_add()`.

Important dependencies:
- Included by common code through the NFS porting layer.
- Exists because the generic code uses Darwin-style KPI names.

Risks and notes:
- Thin macro wrappers directly expose NetBSD mbuf/uio internals; changes in those structures would affect all common NFS code.
