# File Research: sources/os/linux/linux/fs/ntfs3/xattr.c

## Role

Implements NTFS3 extended attributes and xattr handlers, including NTFS EA storage, system xattrs for DOS/NTFS/security attributes, optional POSIX ACL support through EAs, and WSL permission EA compatibility.

## Major Areas

- EA sizing and lookup:
  - `unpacked_ea_size()` and `packed_ea_size()` compute NTFS EA layout sizes.
  - `find_ea()` scans an EA buffer by name.
- EA read/list/get:
  - `ntfs_read_ea()` loads `ATTR_EA_INFO` and `ATTR_EA`, reads resident or nonresident EA data, validates all entries, enforces `$AttrDef` maximums, and marks the volume dirty on inconsistencies.
  - `ntfs_list_ea()` emits xattr names or computes required size.
  - `ntfs_get_ea()` returns a named EA value, supporting size-query semantics and optional external locking.
- EA set/remove:
  - `ntfs_set_ea()` adds, replaces, removes, or no-ops identical EA values.
  - Creates `ATTR_EA_INFO` and `ATTR_EA` if needed.
  - Resizes the EA attribute through `attr_set_size()`.
  - Writes nonresident EA data through run mappings or resident data directly.
  - Updates `NI_FLAG_EA`, parent-update flag, dirty inode state, and optional EA size output.
- POSIX ACL support under `CONFIG_NTFS3_FS_POSIX_ACL`:
  - `ntfs_get_acl()` reads ACL xattrs and caches translated POSIX ACLs.
  - `ntfs_set_acl_ex()` validates symlink/default ACL rules, updates mode for access ACLs, writes ACL xattrs, saves WSL permissions when mode changes, and caches ACLs.
  - `ntfs_set_acl()` and `ntfs_init_acl()` wire VFS ACL operations.
- chmod/list handlers:
  - `ntfs_acl_chmod()` delegates to POSIX ACL chmod when ACLs are enabled.
  - `ntfs_listxattr()` lists NTFS EAs.
- System xattrs:
  - `system.dos_attrib`: one-byte DOS attributes.
  - `system.ntfs_attrib`: little/native u32 file attributes.
  - `system.ntfs_attrib_be`: big-endian u32 file attributes.
  - `system.ntfs_security`: raw NTFS security descriptor by security ID.
- `ntfs_getxattr()`:
  - Handles system xattrs or falls back to NTFS EA lookup.
- `ntfs_setxattr()`:
  - Handles file attribute updates, security descriptor insertion, or generic EA setting.
  - Keeps directory attribute bit consistent with inode mode.
  - For regular files, routes sparse/compressed changes through `ni_new_attr_flags()`.
- WSL compatibility:
  - `ntfs_save_wsl_perm()` writes `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` for device nodes.
  - `ntfs_get_wsl_perm()` reads those EAs to restore uid/gid/mode/rdev.
- Xattr registration:
  - Exposes a single catch-all xattr handler with empty prefix.

## Important Invariants

- EA names are limited to 255 bytes.
- Packed EA size must fit in 16 bits and total EA size must not exceed `sbi->ea_max_size`.
- `ATTR_EA_INFO` and `ATTR_EA` are managed as a pair.
- EA mutation requires `ni_lock()` unless the caller passes `locked=true`.
- ACL xattrs are not supported on symlinks; default ACLs are only meaningful on directories.
- System NTFS security xattr is only supported for NTFS 3.x-style `$Secure` security IDs.
- Every `ntfs_setxattr()` path updates ctime and marks the inode dirty, even when the specific operation returns an error.

## Dependencies

- Uses NTFS attribute APIs, run APIs, inode dirtying, security descriptor helpers, and POSIX ACL APIs.
- Depends on structures from `ntfs.h` and shared declarations from `ntfs_fs.h`.

## Notes For Future Work

- `ntfs_read_ea()` treats malformed EA metadata as a dirty-volume condition; this is an important fsck/chkdsk signal.
- The catch-all xattr handler means name dispatch security must remain strict inside `ntfs_getxattr()` and `ntfs_setxattr()`.
- WSL permission restore trusts internal `$LX*` EA values if all required entries are present.
