# File Research: sources/os/linux/linux/fs/nfsd/Makefile

Builds the Linux kernel NFS server module and optional protocol/layout components.

Key behavior:
- Adds the source directory include path for trace event headers.
- Builds `nfsd.o` when `CONFIG_NFSD` is enabled.
- Compiles `trace.o` first because trace macros are sensitive to include ordering.
- Core NFSD objects include service control, control filesystem, file handles, VFS access, exports, auth, lockd integration, reply cache, stats, file cache, NFSv3 proc/XDR, and netlink.
- Optional objects:
  - NFSv2 procedure/XDR support.
  - NFSv2/NFSv3 ACL support.
  - NFSv4 procedure, XDR, state, idmap, ACL, callback, recovery, and generated XDR support.
  - pNFS layout support and specific block/SCSI/flexfile layout encoders.
  - LOCALIO support.
  - debugfs support.
- Provides an `xdrgen` developer target to regenerate checked-in NFSv4.1 generated XDR files from `Documentation/sunrpc/xdr/nfs4_1.x`.

Important interactions:
- Mirrors the Kconfig feature matrix and determines which NFSD subsystems are linked into the server module.
- Notes that generated XDR files are checked in, so normal builds do not need the generator tooling.
