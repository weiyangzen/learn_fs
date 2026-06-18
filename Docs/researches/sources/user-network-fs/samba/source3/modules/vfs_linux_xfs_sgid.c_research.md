# sources/user-network-fs/samba/source3/modules/vfs_linux_xfs_sgid.c

Purpose: implements the `linux_xfs_sgid` VFS workaround module for a Linux XFS behavior where newly created directories may fail to inherit the SGID bit as Samba expects.

Important APIs/types/functions: the module overrides only `mkdirat` with `linux_xfs_sgid_mkdirat()`. It uses `SMB_VFS_NEXT_MKDIRAT()`, `full_path_from_dirfsp_atname()`, `SMB_VFS_PARENT_PATHNAME()`, `SMB_VFS_NEXT_STAT()`, root privilege elevation, and `SMB_VFS_NEXT_FCHMOD()`.

Control flow: after the downstream `mkdirat` succeeds, the module builds the created path, finds and stats the parent, and returns success unchanged if the parent does not have `S_ISGID` or if follow-up checks fail. If the parent has SGID, it stats the new directory, adds `S_ISGID` to its mode, strips `S_IFDIR` before chmod, temporarily becomes root because Linux XFS may otherwise ignore SGID chmod while returning success, and applies the mode through the next `fchmod`.

State and persistence: no module state is stored. Persistent behavior is limited to setting the SGID mode bit on newly created directories.

Dependencies and integration points: stackable over the normal filesystem module, relies on Samba path helpers and privilege helpers, and assumes `smb_fname->fsp` is valid for the just-created directory chmod path.

Risks: errors after successful mkdir are intentionally logged but do not turn the operation into failure, so callers may see success even when SGID repair failed. The root-elevated chmod is narrow but security-sensitive. Test signals include mkdir under SGID and non-SGID parents, failure to stat parent/new directory, chmod failure while preserving mkdir success, and verifying the mode passed to `FCHMOD` sets SGID without including file-type bits.
