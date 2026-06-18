# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdport.c

Large portability and integration layer between the protocol-level NFS server and NetBSD/FreeBSD-style kernel VFS primitives. It defines global NFS server state, sysctls, reply-cache hash tables and locks, NFSv4 pseudo-root mount state, server module load/unload handling, and many `nfsvno_*` wrappers used by higher-level NFS service code.

The vnode operation wrappers cover attributes, file handles, access checks, setattr, namei/path buffers, readlink, read/write mbuf I/O, create/mknod/mkdir/symlink, remove/rmdir/rename/link, fsync/commit, statfs, NFSv4 open/create, filerev updates, NFSv4 fillattr glue, directory reading, settable attribute decoding, export credential mapping, export checks, file-handle-to-vnode lookup, and optional local advisory locks for NFSv4.

Directory service code is substantial. `nfsrvd_readdir()` builds NFSv2/v3 directory replies from `VOP_READDIR()` results, filters invalid/whiteout entries, handles UFS cookie behavior, enforces reply size, and emits EOF flags. `nfsrvd_readdirplus()` supports NFSv3 readdirplus and NFSv4 readdir attributes, optionally using `VFS_VGET()` or `VOP_LOOKUP()`, handling ZFS snapshot quirks, crossing mount points for NFSv4 when enabled, referrals, rdattr_error, file handles, and attribute reply trimming.

Attribute parsing is split between `nfsrv_sattr()` for NFSv2/v3/v4 dispatch and `nfsv4_sattr()` for NFSv4 attrbit parsing. The NFSv4 parser handles size, ACL, mode, owner, owner_group, access/modify time setting, unsupported attributes, attrlist padding, and BADXDR/ATTRNOTSUPP reporting.

Export and credential logic includes `nfsd_excred()`, `nfsvno_checkexp()`, `nfsvno_fhtovp()`, `nfsd_fhtovp()`, and `nfsvno_testexp()`. It applies root squashing/anonymous exports, AUTH_SYS versus RPCSEC_GSS security flavor checks, v4-only exports, optional fallback for the NFSv4 pseudo root, and NFSv4 traversal of unexported file systems where allowed.

Control paths include `nfssvc_nfsd()` and `nfssvc_srvcall()` for adding sockets, starting nfsd workers, public file handles, v4 root export setup, stable restart file setup, client revoke/dump operations, lock dump operations, stable backup signaling, and suspend/resume of nfsd threads. `nfsd_modevent()` initializes caches, locks, NFS state, service pools, pseudo-root mount state, delegation hooks, and nfssvc callbacks on load; unload refuses while nfsd threads run, discards NFSv4 state, cleans caches, destroys locks, and frees hash tables.

Important implementation risks are mostly lifetime and locking related: vnode lock state must match each VOP call, namei buffers are manually owned, mbuf replies are copied/truncated by protocol size, mount busy references protect cross-mount readdirplus work, and module unload must coordinate NFSv4 state, service pools, reply caches, and global callback pointers.
