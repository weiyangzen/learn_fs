# File Research: sources/virtualization/libblockdev/src/plugins/fs/ntfs.h

Declares NTFS info data and operations.

Key contents:
- Defines `BDFSNtfsInfo` with `label`, `uuid`, `size`, and `free_space`.
- Declares copy/free helpers.
- Declares mkfs, check, repair, label, UUID, info, resize, and minimum-size APIs.

Important invariants:
- NTFS UUID refers to the volume serial number format, not an RFC UUID.
- Returned size/free-space values are byte counts.

Filesystem/block relevance:
- Exposes NTFS management functionality to the generic filesystem plugin.

Notable risks:
- There is a minor declaration formatting inconsistency in `bd_fs_ntfs_check_uuid ( const gchar *uuid, ...)`, but it is semantically harmless.
