# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_util.c

Purpose: `pvfs_util.c` provides small shared helpers for wildcard detection, errno mapping, attribute matching/normalization, file copy, name hashing, and allocation-size rounding.

Important APIs, types, and functions: Public functions are `pvfs_has_wildcard`, `pvfs_map_errno`, `pvfs_match_attrib`, `pvfs_attrib_normalise`, `pvfs_copy_file`, `pvfs_name_hash`, and `pvfs_round_alloc_size`.

Control flow: `pvfs_has_wildcard` checks for SMB wildcard characters. `pvfs_map_errno` uses Samba common Unix-to-NTSTATUS mapping and logs at debug level 10. `pvfs_match_attrib` enforces search/delete attribute inclusion rules for directories, hidden/system files, and must-have attributes. `pvfs_attrib_normalise` removes `FILE_ATTRIBUTE_NORMAL` when other bits are present and synchronizes the directory bit with POSIX mode. `pvfs_copy_file` opens source and destination through PVFS syscall wrappers, copies in 64 KiB chunks, cleans up incomplete destinations, applies mode derived from source DOS attributes, copies DOS metadata, and saves DOS attributes. `pvfs_name_hash` implements case-folded FNV1 over codepoints. `pvfs_round_alloc_size` rounds up to the configured allocation unit.

State and persistence behavior: Most helpers are stateless. `pvfs_copy_file` creates a persistent destination file and xattr-backed DOS metadata, deleting the destination on failure. Hash output feeds stream IDs and short-name mangling.

Dependencies and integration points: Used by rename copy, short-name hashing, stream IDs, metadata save/load, search/unlink/rename filters, and file size reporting. It depends on talloc, POSIX read/write, PVFS syscall wrappers, and xattr DOS attribute saves.

Risks: `pvfs_copy_file` does not copy alternate data streams or ACLs here; it copies DOS attributes only. The write loop retries on EINTR/EAGAIN but does not handle partial positive writes by continuing the remainder. Hash-based stream IDs can collide.

Test signals: Cover wildcard detection, attribute filters, normal attribute normalization for dirs/files, copy cleanup on read/write/chmod/xattr failure, readonly/system/hidden copy metadata, hash case folding, and allocation rounding boundaries.
