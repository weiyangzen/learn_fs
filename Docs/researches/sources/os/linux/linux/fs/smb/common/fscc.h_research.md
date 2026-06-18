# File Research: sources/os/linux/linux/fs/smb/common/fscc.h

## Scope
Read completely: 566 lines. This header defines shared MS-FSCC wire structures and constants used by SMB client and server code.

## Purpose
`fscc.h` maps Microsoft File System Control Codes and file/filesystem information classes into packed Linux C structures. It provides common definitions for reparse points, copy/clone controls, integrity, allocated ranges, file metadata, directory entries, rename/link set-info buffers, filesystem info, DOS attributes, notify actions, and SMB3 POSIX filesystem information.

## Main Definition Areas

## Reparse Data
Defines packed structures for:
- generic reparse data buffers.
- GUID reparse buffers.
- mount point reparse buffers.
- symlink reparse buffers with `SYMLINK_FLAG_RELATIVE`.
- NFS reparse buffers with `NFS_SPECFILE_*` inode type constants.
- WSL/LX symlink reparse buffers.

These are used by SMB reparse-point handling for symlinks, junctions, special files, and WSL interoperability.

## FSCTL Data Structures
Defines buffers for:
- `duplicate_extents_to_file`
- `duplicate_extents_to_file_ex`
- integrity query/set responses and requests.
- allocated range queries.
- file-region queries.
- on-disk volume information.
- zero-data ranges for `FSCTL_SET_ZERO_DATA`.

These support clone/dedupe-like operations, sparse/range management, integrity streams, and volume metadata queries.

## File Information Structures
Defines:
- `struct smb2_file_all_info`
- `FILE_BASIC_INFO`
- `FILE_BOTH_DIRECTORY_INFO`
- `FILE_DIRECTORY_INFO`
- `struct smb2_file_eof_info`
- `FILE_FULL_DIRECTORY_INFO`
- `FILE_ID_FULL_DIR_INFO`
- `struct smb2_file_internal_info`
- `struct smb2_file_link_info`
- `struct smb2_file_network_open_info`
- `struct smb2_file_rename_info`

The link and rename structures use `__struct_group()` plus `static_assert()` so flexible filename data starts exactly after the packed header group.

## Filesystem Information
Defines filesystem info class numbers:
- volume, label, size, device, attribute, control, full size, object id, driver path, sector size.
- SMB3.1.1 POSIX info class `FS_POSIX_INFORMATION`.

Defines structures:
- `FILE_SYSTEM_ATTRIBUTE_INFO`
- `struct smb2_fs_control_info`
- `struct smb2_fs_full_size_info`
- `struct smb3_fs_ss_info`
- `FILE_SYSTEM_SIZE_INFO`
- `struct filesystem_vol_info`
- `FILE_SYSTEM_DEVICE_INFO`
- `FILE_SYSTEM_POSIX_INFO`

Also defines filesystem capability flags such as sparse files, hard links, persistent ACLs, reparse points, named streams, encryption, USN journal, block refcounting, POSIX unlink/rename support, and sector-size flags.

## File Attributes And Notify
Defines DOS/Windows file attribute bits and little-endian variants:
- readonly, hidden, system, directory, archive, normal, temporary, sparse, reparse, compressed, offline, not indexed, encrypted, integrity stream, no-scrub.
- aggregate `FILE_ATTRIBUTE_MASK`.

Defines SMB2 notify action values and `struct file_notify_information`.

## Integration Points
This header is included by SMB client/server protocol code that builds or parses:
- `QUERY_INFO` and `SET_INFO` file metadata.
- `QUERY_DIRECTORY` records.
- close/open returned network open info.
- filesystem statistics queries.
- change notify responses.
- reparse and FSCTL ioctl buffers.
- SMB3 POSIX statfs data.

## Notable Behaviors
- All wire structs are packed and use explicit endian-annotated types.
- Some legacy CIFS and SMB2 structures with similar names are intentionally not identical; comments call out differences.
- Several structures end in flexible arrays for variable path/name/security data.
- `FILE_SYSTEM_POSIX_INFO` follows the Samba SMB3 POSIX extension document rather than base MS-FSCC alone.

## Risks And Review Focus
- Wire layout drift is the primary risk; packed offsets must match protocol specifications.
- Flexible arrays require callers to validate server-provided lengths before access.
- Rename/link structures depend on `static_assert()` to catch accidental header layout changes.
- Attribute and filesystem capability flags are shared with user-visible behavior such as xattrs, statfs, fallocate, clone, symlink/reparse handling, and cache policy.

## Research Takeaways
`fscc.h` is the SMB common vocabulary for file and filesystem metadata. Most high-level SMB client operations eventually consume or produce one of these packed structures.
