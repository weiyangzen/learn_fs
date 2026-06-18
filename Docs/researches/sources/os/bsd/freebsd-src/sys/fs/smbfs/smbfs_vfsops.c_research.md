# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_vfsops.c

FreeBSD SMBFS VFS operation layer for mounting, unmounting, root lookup, quota stubs, initialization, and filesystem statistics.

Key responsibilities:
- Registers the `smbfs` VFS with `VFCF_NETWORK` and module dependencies on `netsmb`, `libiconv`, and `libmchain`.
- Exposes `vfs.smbfs.version` and writable `vfs.smbfs.debuglevel` sysctls.
- Converts legacy `smbfs_args` from `smbfs_cmount()` into nmount-style options after validating `SMBFS_VERSION`.
- Mounts an already-established netsmb session via the `fd` option, resolves it to an `smb_share`/`smb_dev`, stores a new `struct smbmount`, and synthesizes `f_mntfromname` as `//user@server/share`.
- Parses mount policy options for uid, gid, file mode, directory mode, case conversion, and long-name behavior.
- Creates and caches the root smbnode using `smbfs_smb_lookup(NULL, NULL, 0, ...)` and `smbfs_nget()`, marking the root vnode with `VV_ROOT`.
- Unmounts by repeatedly calling `vflush()` while parent references are being released, then drops the SMB share/device references and frees mount-private state.
- Initializes and destroys the global `smbfs_pbuf_zone` with `pbuf_zsecond_create()` and `uma_zdestroy()`.
- Implements `smbfs_statfs()` by delegating space queries to `smbfs_smb_statfs()` and using the VC transmit maximum as the I/O size.

Dependencies:
- VFS mount, vnode, sysctl, UMA, pbuf, module, and mount option infrastructure.
- netsmb session/share/device APIs: `smb_dev2share()`, `smb_share_unlock()`, `smb_share_lock()`, `smb_share_put()`, `sdp_trydestroy()`, `SSTOVC()`, and `smb_makescred()`.
- SMBFS node and subroutine helpers: `VFSTOSMBFS`, `smbfs_nget()`, `smbfs_smb_lookup()`, `smbfs_smb_statfs()`, and SMB credential allocation/free helpers.

Notable risks:
- Mount depends on a userspace-provided session file descriptor; option validation and lifetime transfer through `smb_dev2share()` are critical.
- Error paths must keep `smb_share`, `smb_dev`, `smbmount`, and SMB credential lifetimes balanced.
- `smbfs_unmount()` relies on `sm_didrele` progress to resolve child-to-parent vnode references; incorrect release accounting could leave busy mounts.
- `f_mntfromname` construction uses bounded `strncpy()` and pointer arithmetic; truncation is intended but must avoid overruns.
