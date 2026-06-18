# File Research: sources/os/linux/linux/fs/smb/server/smbacl.c

Implements translation between Windows security descriptors/SIDs/ACEs and Linux ownership, mode bits, POSIX ACLs, and ksmbd NTACL xattrs.

Key behaviors:
- Defines built-in SIDs for ksmbd domain, creator owner/group, everyone, authenticated users, Unix users/groups, and NFS-style UID/GID/mode SIDs.
- Compares and copies SIDs, maps Unix IDs to SIDs, and maps SIDs back to `kuid_t`/`kgid_t` through mount idmaps.
- Converts SMB access masks to POSIX mode bits and POSIX mode bits to SMB access masks.
- Parses DACLs defensively with bounds checks on ACL size, ACE count, SID subauthority count, and ACE sizes.
- Builds POSIX ACL state from recognized owner/group/everyone/named-user ACEs and optional default ACLs for directories.
- Builds Windows security descriptors from inode owner/group/mode and POSIX ACLs, optionally preserving existing NT DACL entries.
- Computes scratch length for security descriptor construction with overflow checks.
- Inherits DACLs from parent NTACL xattrs, handling creator owner/group substitution, inheritance flags, no-propagate behavior, and directory/file differences.
- Checks requested access against stored Windows ACL xattrs, falling back through POSIX ACL entries and everyone ACEs.
- Applies `SET_INFO` security changes by parsing incoming descriptors, updating inode uid/gid/mode, setting POSIX ACLs, and persisting NTACL xattrs when share config enables ACL xattrs.
- Initializes the server domain SID from user-space startup subauthorities.

Dependencies:
- Uses VFS xattr helpers from `vfs.c`, access mapping from `smb_common.c`, share config flags, POSIX ACL APIs, and mount idmapping APIs.

Role in subsystem:
- Primary security semantic bridge for ksmbd. It lets Windows clients see and update NT-style ACLs while keeping Linux inode metadata and POSIX ACLs coherent.
