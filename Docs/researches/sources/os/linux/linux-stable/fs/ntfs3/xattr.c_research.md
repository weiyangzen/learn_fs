# File Research: sources/os/linux/linux-stable/fs/ntfs3/xattr.c

Purpose: Implements NTFS3 extended attributes, special system xattrs, POSIX ACL storage via EAs, and WSL permission/device metadata.

Key responsibilities:
- Defines supported special xattr names: `system.dos_attrib`, `system.ntfs_attrib`, `system.ntfs_attrib_be`, and `system.ntfs_security`.
- Reads and validates packed NTFS EA data through `ntfs_read_ea()`, including EA_INFO/EA pairing, size limits from `$AttrDef`, resident/nonresident reads, and per-entry consistency checks.
- Lists, gets, sets, replaces, and removes NTFS EAs with `ntfs_list_ea()`, `ntfs_get_ea()`, and `ntfs_set_ea()`.
- Creates/deletes `ATTR_EA_INFO` and `ATTR_EA`, resizes EA storage, writes resident or nonresident content, updates EA flags, parent-update flags, and inode dirty state.
- Under `CONFIG_NTFS3_FS_POSIX_ACL`, maps POSIX ACLs to xattrs and implements get/set/init/chmod helpers.
- Implements generic `listxattr`, getxattr, and setxattr dispatch.
- Gets/sets NTFS DOS attributes and full NTFS attributes, preserving directory-bit consistency and invoking `ni_new_attr_flags()` for sparse/compressed regular-file transitions.
- Gets/sets NTFS security descriptors through `$Secure` by security id on NTFS 3.x volumes.
- Saves and restores WSL metadata EAs `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV`.

Important invariants:
- EA names are limited to 255 bytes.
- EA packed size must fit 16 bits and total EA size must not exceed `sbi->ea_max_size`.
- Setting the final EA removes both `ATTR_EA_INFO` and `ATTR_EA` and clears `NI_FLAG_EA`.
- Changes in packed EA size set `NI_FLAG_UPDATE_PARENT`, because parent directory duplicate information may need updating.
- POSIX ACLs are not applied to symlinks; default ACLs are only valid on directories.
- `system.ntfs_security` requires NTFS 3.x and valid relative security descriptors.

Dependencies:
- Uses attribute and run APIs from `attrib.c`/`run.c`, inode and record helpers, `$Secure` helpers, POSIX ACL helpers, and VFS xattr infrastructure.

Risk notes:
- `ntfs_read_ea()` marks the volume dirty on malformed EA data.
- Some getxattr undersized-buffer cases return `-ENODATA` rather than the more typical `-ERANGE`, matching this driver's current behavior.
- `ntfs_setxattr()` updates ctime and marks the inode dirty even when the final operation returns an error.
