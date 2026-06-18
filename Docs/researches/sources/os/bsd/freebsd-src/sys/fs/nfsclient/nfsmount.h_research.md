# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfsmount.h

## Purpose
Defines `struct nfsmount`, the per-mount state object for FreeBSD's new NFS client, plus mount-private flags, kernel-only new mount flags, and field/offset helper macros.

## Main Data
- Embeds `struct nfsmount_common nm_com` for shared NFS/NLM mount state such as lock, flags, state, timeout, hostname, mount pointer, and callback hooks.
- Stores root file handle, socket/RPC request state, timeout counters, negotiated read/write/readdir sizes, readahead, commit sizing, attr-cache lifetimes, write verifier, async I/O queue accounting, max file size, and namecache timeouts.
- Adds NFSv4/newnfs state: session list, client pointer, TLS certificate name, mount UID, client-id discriminator, NFSv4 fsid, minor version, `nconnect` additional clients, clone block size, and variable-length Kerberos/dirpath/server-principal storage.

## Main Macros And Flags
- `NFS_MAXNCONN` caps `nconnect` at 16.
- Field aliases expose common/socket fields as direct `nm_*` names, including `nm_nam`, `nm_sotype`, `nm_client`, `nm_mtx`, `nm_flag`, `nm_state`, `nm_mountp`, and callbacks.
- Private flags include forced dismount, cancel RPCs, I/O advise through MDS, disabled copy/consecutive-copy/seek/xattr/advise/allocate/deallocate, delegation-issued tracking, and fake-root-file-handle mode.
- New kernel-only mount flags include `NFSMNT_TLS` and `NFSMNT_SYSKRB5`.
- `NFSMNT_DIRPATH()` and `NFSMNT_SRVKRBNAME()` compute offsets into trailing variable-length name storage.
- `VFSTONFS(mp)` converts a mount to its `struct nfsmount`.

## Integration
Consumed by mount setup, VFS/vnode operations, RPC connection logic, NFSv4 state/session code, pNFS layout/data-server paths, lockd/NLM integration, and mount option reporting.

## Risks
- The trailing `nm_name[1]` allocation must be sized and indexed consistently with `nm_krbnamelen`, `nm_dirpathlen`, and `nm_srvkrbnamelen`.
- Additional `nconnect` RPC clients are protected through `nm_sockreq.nr_mtx`; users must preserve that lock discipline.
- Private flags are used as mount-wide capability disablement after protocol failures, so accidental setting can permanently degrade a mount until remount.
