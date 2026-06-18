# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_export.c

## Purpose
Implements generic VFS export management for NFS/WebNFS-style filesystem exports. It stores per-mount export policies, address-based export credentials, public filesystem metadata, jail-scoped export ownership, and export access checks.

## Main Elements
- Export data structures:
  - `struct netcred` stores radix nodes, export flags, anonymous credential, and accepted security flavors.
  - `struct netexport` stores a default export plus IPv4 and IPv6 radix trees.
  - Static `nfs_pub` stores the single public WebNFS export.
- Address-list construction:
  - `vfs_hang_addrlist()` installs default or address-specific export entries from `struct export_args`.
  - Default exports populate `ne_defexported` and set `MNT_DEFEXPORTED`.
  - Address exports copy in user-supplied sockaddr and optional mask, create AF_INET/AF_INET6 radix heads as needed, add the entry, and build an anonymous credential rooted in `prison0`.
  - If `ex_numsecflavors` is zero in `vfs_export()`, AUTH_SYS is installed as the default flavor.
- Address-list cleanup:
  - `vfs_free_netcred()` deletes radix entries and frees anonymous credentials.
  - `vfs_free_addrlist_af()` walks and destroys one address-family radix tree.
  - `vfs_free_addrlist()` frees IPv4/IPv6 lists and the default anonymous credential.
- Export update/delete:
  - `vfs_export()` validates add/delete flags, serializes on `mnt_explock`, creates or resets `mnt_export`, manages `MNT_EXPORTED`, `MNT_DEFEXPORTED`, and `MNT_EXPUBLIC`, and records the jail credential owning the export when applicable.
  - Delete paths remove public export state, free address lists, clear mount flags, drop jail credentials, and decrement the prison export count.
  - It removes the transient `"export"` mount option from current and new mount option lists after processing.
- Jail cleanup:
  - `vfs_exjail_delete()` is called during prison cleanup to find mounts exported by the prison, invalidate or delete those exports, drop credential references, and clear export flags so the prison can be released.
- Public filesystem:
  - `vfs_setpublicfs()` installs or clears the single public filesystem.
  - On install it gets the mount root vnode, obtains a file handle, records the mount fsid, and optionally copies and validates an index filename.
- Export lookup and access checks:
  - `vfs_export_lookup()` matches a client sockaddr against the mount's AF-specific radix tree and falls back to the default export.
  - `vfs_stdcheckexp()` is the generic export verifier used after filesystem file-handle validation. It returns export flags, holds the anonymous credential, and copies security flavors for the caller.

## Dependencies And Integration
Uses mount export locks and flags, radix trees, socket address families, credentials and prison references, NFS public-export structures, `VFS_ROOT()`, `VOP_VPTOFH()`, copyin/copyinstr from user export arguments, and mount option helpers. Filesystems use `vfs_stdcheckexp()` as the generic authorization half of file-handle-to-vnode export checks after validating filesystem-specific file handles.

## Risk Notes
Export state is security-sensitive because it determines remote filesystem access. Correctness depends on `mnt_explock` serialization, jail ownership checks, proper credential reference management, radix tree cleanup, and careful distinction between host-root and jailed export deletion. Address and mask lengths are constrained but copied from userspace, and only one public filesystem can be active. A notable implementation quirk is that anonymous export credentials are synthesized manually from uid/groups and then attached to `prison0`.
