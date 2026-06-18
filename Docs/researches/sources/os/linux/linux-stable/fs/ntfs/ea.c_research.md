# File Research: sources/os/linux/linux-stable/fs/ntfs/ea.c

## Scope

This file implements NTFS extended attributes, Linux xattr handlers, WSL metadata EAs, DOS/NTFS attribute xattrs, and optional POSIX ACL storage. It bridges NTFS `$EA` / `$EA_INFORMATION` attributes to Linux VFS xattr and ACL APIs.

## APIs And Control Flow

- `ntfs_write_ea()` opens a fake attribute inode for `$EA` or `$EA_INFORMATION`, writes via `ntfs_inode_attr_pwrite()`, optionally truncates the target attribute, and marks the base MFT record dirty.
- `ntfs_ea_lookup()` scans packed `struct ea_attr` records, validating `next_entry_offset`, name/value sizing, alignment, and bounds before returning an EA offset and size.
- `ntfs_get_ea()` reads `$EA_INFORMATION`, checks `ea_query_length`, reads `$EA`, finds a named EA, and returns either the value length or copied value.
- `ntfs_set_ea()` creates, replaces, appends, or removes EAs while maintaining `$EA_INFORMATION` fields:
  - `ea_length` tracks packed EA size.
  - `ea_query_length` tracks aligned query length.
  - `need_ea_count` is decremented when removing `NEED_EA` entries.
  - `$EA_INFORMATION` is written first during replacement/removal so failure modes can be partially constrained.
- WSL helpers map Unix-like metadata to fixed EA names:
  - `$LXUID`, `$LXGID`, `$LXMOD`, `$LXDEV`.
  - `ntfs_ea_get_wsl_inode()` loads uid/gid/mode/device unless mount options override uid/gid.
  - `ntfs_ea_set_wsl_inode()` stores selected uid/gid/mode/device values.
- `ntfs_listxattr()` enumerates EA names and returns the Linux xattr name list format.
- `ntfs_getxattr()` handles synthetic system names `system.dos_attrib`, `system.ntfs_attrib`, and `system.ntfs_attrib_be`, falling back to NTFS EAs for other names.
- `ntfs_new_attr_flags()` changes sparse/compressed attribute flags for regular files, resizing the attribute record layout when the non-resident compressed-size field is added or removed.
- `ntfs_setxattr()` handles synthetic DOS/NTFS file attribute writes, updates readonly mode bits, marks filename metadata dirty, or delegates ordinary xattrs to `ntfs_set_ea()`.
- `ntfs_xattr_handlers` exposes one catch-all xattr handler with an empty prefix.
- Under `CONFIG_NTFS_FS_POSIX_ACL`, POSIX ACLs are serialized to xattrs, cached through VFS ACL helpers, and mode changes are also persisted through the WSL `$LXMOD` EA.

## State And Dependencies

Important state includes `NInoHasEA`, `$EA_INFORMATION`, `$EA`, inode mode/uid/gid fields, NTFS file attribute flags, resident/non-resident attribute records, and optional cached ACLs.

This file depends on attribute helpers (`ntfs_attr_readall`, `ntfs_attr_add`, `ntfs_attr_remove`, `ntfs_attr_truncate`, `ntfs_attr_record_resize`), fake attribute inode I/O, POSIX ACL xattr conversion, and VFS xattr handler contracts.

## Risks And Invariants

- `$EA_INFORMATION.ea_query_length` must never exceed the actual `$EA` attribute size; violations are treated as `-EIO`.
- EA record walking relies on both aligned record sizes and `next_entry_offset`; malformed records must not be allowed to run past the EA buffer.
- `ntfs_set_ea()` updates/removes old records before appending replacements, so error handling can leave partially updated attributes if lower-level writes fail.
- Sparse and compressed flags are mutually exclusive in this code path; changing them on non-empty non-resident files is rejected.
- Ordinary xattr setting updates ctime and marks the inode dirty even when the delegated EA operation returns an error.
- ACL writes attempt rollback of the ACL EA if updating `$LXMOD` fails.
